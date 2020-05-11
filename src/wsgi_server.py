import socket
import urllib.parse
from threading import Thread


def worker(conn, wsgi_app, env):
    with conn:
        headers = None
        status_code = None

        def start_response(s, h):
            nonlocal headers, status_code
            status_code = s
            headers = h

        wsgi_response = wsgi_app(env, start_response)

        if headers is None or status_code is None:
            conn.sendall(b'HTTP/1.1 500\r\n\r\nInternal Server Error\n')
            return

        print(f"{env['REMOTE_ADDR']} - {status_code}")
        status_line = f"HTTP/1.1 {status_code}".encode("utf-8")
        headers = [f"{k}: {v}" for k, v in headers]

        response_body = b""
        content_length = 0
        for b in wsgi_response:
            response_body += b
            content_length += len(b)
        headers.append(f"Content-Length: {content_length}")
        header_bytes = "\r\n".join(headers).encode("utf-8")
        env["wsgi.input"].close()  # close() does not raise an exception if called twice.
        conn.sendall(status_line + b"\r\n" + header_bytes + b"\r\n\r\n" + response_body)


def make_wsgi_environ(rfile, client_address, port):
    # should return '414 URI Too Long' if line is longer than 65536.
    raw_request_line = rfile.readline(65537)
    method, path, version = str(raw_request_line, 'iso-8859-1').rstrip(
        '\r\n').split(' ', maxsplit=2)
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
        'SERVER_PORT': port,
        'REMOTE_ADDR': client_address[0],
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

        key, value = line.decode('iso-8859-1').rstrip("\r\n").split(":",
                                                                    maxsplit=1)
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


def serve_forever(app, host="127.0.0.1", port=8000,
                  max_accept=128, timeout=30.0, rbufsize=-1):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.bind((host, port))
        sock.listen(max_accept)

        while True:
            conn, client_address = sock.accept()
            conn.settimeout(timeout)
            rfile = conn.makefile('rb', rbufsize)
            env = make_wsgi_environ(rfile, client_address, port)
            Thread(target=worker, args=(conn, app, env), daemon=True).start()


if __name__ == '__main__':
    from main import app
    serve_forever(app)
