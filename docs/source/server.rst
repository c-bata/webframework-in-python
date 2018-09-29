WIP: WSGIサーバーのつくりかた
=================================

WSGIアプリケーションフレームワークとして最低限必要な機能をある程度実装しました。
200行弱のフレームワークですが、ルーティングやリクエストオブジェクト、レスポンスオブジェクトを実装したことで、
WSGIのインターフェイスよりは随分使いやすくなりました。

次はHTTP 1.xの解説も兼ねて、WSGIサーバーの作り方についてお話します。
作るのは150行に満たないWSGIサーバーですが、手元のDjangoアプリケーションも問題なく動かすことができました。
パフォーマンスや脆弱性の問題を抱えてはいますが、動作を理解するにはうってつけです。


ソケットモジュールを使ったTCP通信
---------------------------------

日頃の業務の中で、TCPのsocket通信プログラムを書くことはあまりないかもしれません。
もし難しければ定型文として、覚えてもらっても大丈夫です。

.. code-block:: python

   import socket

   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
       sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
       sock.bind(('127.0.0.1', 8000))
       sock.listen(1)

       while True:
           conn, client_address = sock.accept()
           with conn:
               raw_request = b''
               while True:
                   chunk = conn.recv(4096)
                   raw_request += chunk
               chunk = conn.recv(100)
               rfile = conn.makefile('rb', self.rbufsize)

               conn.sendall(b'Hello')


なにかリクエストを受け取ったら ``Hello`` とだけ返し、接続を終了するシンプルなプログラムです。


HTTP レスポンスを返す
----------------------------------

.. code-block:: python

   import socket
   from threading import Thread


   def run_server(address):
       with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
           sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
           sock.bind(address)
           sock.listen(5)

           while True:
               conn, client_address = sock.accept()
               print("Connection", client_address)
               Thread(target=http_handler, args=(conn,), daemon=True).start()


   def http_handler(conn):
       rfile = conn.makefile('rb', -1)
       while True:
           line = rfile.readline()
           if line == b'\r\n':
               break  # end of request header

       print(line.decode('iso-8859-1'), end="")
       rfile.close()
       conn.sendall(b'HTTP/1.1 501\r\n\r\nNot Implemented\r\n')


   if __name__ == '__main__':
       run_server(('127.0.0.1', 8000))

ブラウザーで開いてみてください。


クラスに載せる
----------------------------------

.. code-block:: python

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
       def __init__(self, host="127.0.0.1", port=8000):
           self.host = host
           self.port = port

       def run_forever(self):
           with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
               sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
               sock.bind((self.host, self.port))
               sock.listen(5)

               while True:
                   conn, client_address = sock.accept()
                   with conn:
                       conn.sendall(b'HTTP/1.1 501\r\n\r\nNot Implemented\r\n')


   if __name__ == '__main__':
       serv = WSGIServer()
       serv.run_forever()



