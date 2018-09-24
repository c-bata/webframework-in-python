import socket


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
                with conn:
                    conn.sendall(b'HTTP/1.1 501\r\n\r\nNot Implemented\r\n')


if __name__ == '__main__':
    from main import app
    serv = WSGIServer(app)
    serv.run_forever()
