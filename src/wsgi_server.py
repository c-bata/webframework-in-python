import socket
import urllib.parse
from threading import Thread


class ResponseWriter:
    def __init__(self):
        self.headers = None
        self.status_code = None

    def start_response(self, status_code, headers):
        self.status_code = status_code
        self.headers = headers

    @property
    def called(self):
        return self.headers is not None and self.status_code is not None


def worker(conn, wsgi_app, env):
    with conn:
        response = ResponseWriter()
        wsgi_response = wsgi_app(env, response.start_response)
        print(f"{env['REMOTE_ADDR']} - {response.status_code}")
        if not response.called:
            conn.sendall(b'HTTP/1.1 501\r\n\r\nSorry\n')
            return

        status_line = f"HTTP/1.1 {response.status_code}".encode("utf-8")
        headers = [f"{k}: {v}" for k, v in response.headers]

        response_body = b""
        content_length = 0
        for b in wsgi_response:
            response_body += b
            content_length += len(b)
        headers.append(f"Content-Length: {content_length}")
        header_bytes = "\r\n".join(headers).encode("utf-8")
        env["wsgi.input"].close()  # this doesn't raise error if close twice.
        conn.sendall(status_line + b"\r\n" + header_bytes + b"\r\n\r\n" + response_body)


class WSGIServer:
    def __init__(self, app, host="127.0.0.1", port=8000,
                 max_accept=128, timeout=10.0, rbufsize=-1):
        self.app = app
        self.host = host
        self.port = port
        self.max_accept = max_accept
        self.timeout = timeout
        self.rbufsize = rbufsize

    def make_wsgi_environ(self, rfile, client_address):
        # should return '414 URI Too Long' if line is longer than 65536.
        raw_request_line = rfile.readline(65537)
        method, path, version = str(raw_request_line, 'iso-8859-1').rstrip('\r\n').split(' ', maxsplit=2)
        if '?' in path:
            path, query = path.split('?', 1)
        else:
            path, query = path, ''

        env = {
            'REQUEST_METHOD': method,
            'PATH_INFO': urllib.parse.unquote(path, 'iso-8859-1'),
            'QUERY_STRING': query,
            'SERVER_PROTOCOL': "HTTP/1.1",
            'SERVER_NAME': socket.getfqdn(),
            'SERVER_PORT': self.port,
            'REMOTE_ADDR': client_address,
            'SCRIPT_NAME': "",
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': "http",
            'wsgi.multithread': True,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }

        while True:
            # should return '431 Request Header Fields Too Large'
            # if line is longer than 65536 or header exceeds 100 lines.
            line = rfile.readline(65537)
            if line in (b'\r\n', b'\n', b''):
                break

            key, value = line.decode('iso-8859-1').rstrip("\r\n").split(":", maxsplit=1)
            value = value.lstrip(" ")
            if key.upper() == "CONTENT-TYPE":
                env['CONTENT_TYPE'] = value
            if key.upper() == "CONTENT-LENGTH":
                env['CONTENT_LENGTH'] = value
            env_key = "HTTP_" + key.replace("-", "_").upper()
            if env_key in env:
                env[env_key] = env[env_key] + ',' + value
            else:
                env[env_key] = value
        env['wsgi.input'] = rfile
        return env

    def run_forever(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            sock.bind((self.host, self.port))
            sock.listen(self.max_accept)

            while True:
                conn, client_address = sock.accept()
                conn.settimeout(self.timeout)
                rfile = conn.makefile('rb', self.rbufsize)
                env = self.make_wsgi_environ(rfile, client_address)
                Thread(target=worker, args=(conn, self.app, env), daemon=True).start()


if __name__ == '__main__':
    from main import app
    serv = WSGIServer(app)
    serv.run_forever()
