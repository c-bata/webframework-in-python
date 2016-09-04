リクエスト・レスポンス
===========

前節にて、ルーティングの実装が完了しました。


WSGI Environment
----------------

WSGIのアプリケーションの第一引数には、各種リクエストの情報が含まれています。
しかしこの辞書型のオブジェクトから、様々な情報を取り出すのは少し大変でしょう。
またviewの関数


Requestをラップする
-------------

厳密にはWSGIのEnvironをラップします。

.. code-block:: python

   class Request:
       def __init__(self, environ):
           self.environ = environ

各view関数には、envの代わりにbodyを渡しましょう。

.. code-block:: python

   class App:
       (中略)
       def __call__(self, env, start_response):
           callback, kwargs = self.router.match(env)
           request = Request(env)
           return callback(request, start_response, **kwargs)

これでRequestがview関数に渡せるようになりました。
しかしRequestクラスには何も実装していません。
リクエストボディを読み取りましょう。


.. code-block:: python

   @property
   def body(self) -> str:
       if self._body is None:
           content_length = int(self.environ.get('CONTENT_LENGTH', 0))
           self._body = self.environ['wsgi.input'].read(content_length).decode('utf-8')
       return self._body


`request.body` と呼び出すだけで、bodyを取り出すことが出来ました。
curlでjsonを叩いてみましょう。


.. todo:: curlでリクエスト


Responseをラップする
--------------

