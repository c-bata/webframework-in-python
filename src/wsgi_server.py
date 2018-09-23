import io
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
        conn.sendall(status_line + b"\r\n" + header_bytes + b"\r\n\r\n" + response_body)


class WSGIServer:
    def __init__(self, app, host="127.0.0.1", port=8000, max_accept=128, max_read=4096):
        self.app = app
        self.host = host
        self.port = port
        self.max_accept = max_accept
        self.max_read = max_read

    def make_wsgi_environ(self, conn, client_addr):
        raw_request = b''
        content_length = 0
        while True:
            chunk = conn.recv(self.max_read)
            raw_request += chunk
            content_length += len(chunk)
            if len(chunk) < self.max_read:
                break

        header_bytes, body = raw_request.split(sep=b'\r\n\r\n', maxsplit=1)
        headers = header_bytes.decode('utf-8').splitlines()
        request_line = headers[0]
        headers = headers[1:]
        method, path, proto = request_line.split(' ', maxsplit=2)
        if '?' in path:
            path, query = path.split('?', 1)
        else:
            path, query = path, ''
        env = {
            'REQUEST_METHOD': method,
            'PATH_INFO': urllib.parse.unquote(path, 'iso-8859-1'),
            'QUERY_STRING': query,
            'SERVER_PROTOCOL': "HTTP/1.1",
            'SERVER_NAME': self.host,
            'SERVER_PORT': self.port,
            'REMOTE_ADDR': f"{client_addr[0]}:{client_addr[1]}",
            'wsgi.url_scheme': "http",
            'wsgi.input': io.BytesIO(body),
            'wsgi.multithread': True,
            'wsgi.version': (1, 0, 1),
        }
        for l in headers:
            key, value = l.split(":", maxsplit=1)
            env_key = "HTTP_" + key.replace("-", "_").upper()
            if env_key in env:
                env[env_key] = env[env_key] + ',' + value
            else:
                env[env_key] = value
        return env

    def run_forever(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            sock.bind((self.host, self.port))
            sock.listen(self.max_accept)

            while True:
                conn, client_addr = sock.accept()
                env = self.make_wsgi_environ(conn, client_addr)
                Thread(target=worker, args=(conn, app, env), daemon=True).start()


if __name__ == '__main__':
    from main import app
    serv = WSGIServer(app)
    serv.run_forever()
