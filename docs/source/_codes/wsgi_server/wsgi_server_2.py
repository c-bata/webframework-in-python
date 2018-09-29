import socket
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


def worker(wsgi_app, env):
    response = ResponseWriter()
    wsgi_response = wsgi_app(env, response.start_response)
    if not response.called:
        return b'HTTP/1.1 500\r\n\r\Internal Server Error\n'

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
    return status_line + b"\r\n" + header_bytes + b"\r\n\r\n" + response_body


class WSGIServer:
    def __init__(self, app, host="127.0.0.1", port=8000):
        self.app = app
        self.host = host
        self.port = port

    def run_forever(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            sock.bind((self.host, self.port))
            sock.listen(1)

            while True:
                conn, client_address = sock.accept()
                env = {
                    'REQUEST_METHOD': "GET",
                    'PATH_INFO': "/",
                    'QUERY_STRING': "",
                    'REMOTE_ADDR': client_address[0],
                }
                with conn:
                    response = worker(self.app, env)
                    conn.sendall(response)


if __name__ == '__main__':
    from main import app
    serv = WSGIServer(app)
    serv.run_forever()


def run_server(wsgi_app, address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.bind(address)
        sock.listen(5)

        while True:
            conn, client_address = sock.accept()
            print("Connection", client_address)
            Thread(target=echo_handler, args=(wsgi_app, conn), daemon=True).start()


def echo_handler(wsgi_app, conn):
    with conn:
        rfile = conn.makefile('rb', -1)
        while True:
            line = rfile.readline()
            if line == b'\r\n':
                break  # end of request header
            print(line.decode('iso-8859-1'), end="")
        rfile.close()

        env = {
            'REQUEST_METHOD': "GET",
            'PATH_INFO': "/",
            'QUERY_STRING': "",
        }

        start_response = lambda status_code, headers: print(status_code, headers)
        body = wsgi_app(env, start_response)
        for b in body:
            conn.sendall()

        conn.sendall(b'HTTP/1.1 501\r\n\r\nNot Implemented\r\n')


if __name__ == '__main__':
    from main import app
    run_server(app, ('127.0.0.1', 8000))
