import socket
from threading import Thread


def http_handler(conn):
    with conn:
        rfile = conn.makefile('rb', -1)
        while True:
            line = rfile.readline()
            if line == b'\r\n':
                break  # end of request header
        print(line.decode('iso-8859-1'), end="")
    rfile.close()
    conn.sendall(b'HTTP/1.1 501\r\n\r\nNot Implemented\r\n')


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
                print("Connection", client_address)
                Thread(target=http_handler, args=(conn,), daemon=True).start()


if __name__ == '__main__':
    from main import app
    serv = WSGIServer(app)
    serv.run_forever()
