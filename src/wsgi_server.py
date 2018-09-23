import io
import socket


class ResponseWriter:
    def __init__(self, conn, http_version=1.1):
        self.conn = conn
        self.start_response = False
        self.http_version = http_version

    def __call__(self, status_code, headers):
        if self.start_response:
            raise Exception("Do not call start_response twice")

        self.status_code = status_code
        self.headers = headers
        self.start_response = True

    def write(self, iter_body):
        if not self.start_response:
            raise Exception("start_response should be called once")

        status_num, status_msg = self.status_code.split(" ", maxsplit=1)
        status_line = f"HTTP/{self.http_version} {status_num}".encode('utf-8')

        header_lines = b""
        for k, v in self.headers:
            header_lines += f"{k}: {v}".encode("utf-8")
            header_lines += b"\r\n"

        response_body = b""
        content_length = 0
        for b in iter_body:
            response_body += b
            content_length += len(b)
        response_body += b"\r\n"

        self.conn.sendall(status_line + b"\r\n" + header_lines + b"\r\n" + response_body)


def make_wsgi_environ(conn, host, port):
    raw_request = b''
    while True:
        chunk = conn.recv(4096)
        raw_request += chunk
        if len(chunk) < 4096:
            break

    header_bytes, body = raw_request.split(sep=b'\r\n\r\n', maxsplit=1)
    headers = header_bytes.decode('utf-8').splitlines()
    request_line = headers[0]
    headers = headers[1:]
    method, path, proto = request_line.split(' ', maxsplit=2)

    request = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'SERVER_PROTOCOL': proto,
        'HTTP_HOST': f"{host}:{port}" if port else host,
        'SERVER_PORT': port,
        'wsgi.url_scheme': "http",
        'wsgi.input': io.BytesIO(body),
    }
    for l in headers:
        key, value = l.split(":", maxsplit=1)
        request[key.upper()] = value
    return request


class WSGIServer:
    def __init__(self, app, host="127.0.0.1", port=8000, max_read=4096):
        self.app = app
        self.host = host
        self.port = port
        self.max_read = max_read
        self.max_accept = 1

    def run_forever(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(self.max_accept)

            while True:
                conn, addr = s.accept()

                with conn:
                    env = make_wsgi_environ(conn, self.host, self.port)
                    response = ResponseWriter(conn)
                    response_body = self.app(env, response)
                    response.write(response_body)


if __name__ == '__main__':
    from main import app
    serv = WSGIServer(app)
    serv.run_forever()
