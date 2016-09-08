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
       :
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

次に気になるのは、ヘッダ情報の管理が面倒です。
もう少し簡単に管理できるように、Response情報をラップするクラスを用意してみましょう。

またView関数の責務も考えます。
これまでのView関数は `env` や `start_response` , URL変数を受け取って、WSGIのResponseと同じように
yieldするとbytesのオブジェクトを返すようなオブジェクトを返していました。

今回からは、requestを受け取ってresponseを返すとしっかり決めてしまいましょう。
各View関数でResponseのオブジェクトを生成します。


.. code-block:: python

   @app.route('^/users/(?P<user_id>\d+)/$')
   def user_detail(request, user_id):
       res = 'Hello user {user_id}'.format(user_id=user_id)
       response = Response(body=[res.encode('utf-8')],
                           headers={'Content-type': 'text/plain; charset=utf-8'})
       return response


Responseクラスは次のようになります

.. code-block:: python

   class Response:
       default_status = '200 OK'
       default_content_type = 'text/html; charset=UTF-8'

       def __init__(self, body='', status=None, headers=None):
           self.body = body
           self.status = status or self.default_status
           self.headers = Headers()

           if headers:
               for name, value in headers.items():
                   self.headers.add_header(name, value)

       @property
       def header_list(self):
           if 'Content-Type' not in self.headers:
               self.headers.add_header('Content-Type', self.default_content_type)
           out = [(key, value)
                  for key in self.headers.keys()
                  for value in self.headers.get_all(key)]
           return [(k, v.encode('utf8').decode('latin1')) for (k, v) in out]

   class App:
       :
       def __call__(self, env, start_response):
           callback, kwargs = self.router.match(env)
           request = Request(env)
           response = callback(request, **kwargs)
           start_response(response.status, response.header_list)
           return response.body



チューニング
------

RequestやResponseのクラスはリクエストがある度に、生成されているためパフォーマンスに大きく影響していそうです。
ここでは `__slots__` 属性を用いることでメモリを大幅に節約することが出来ます。
試してみましょう。


Before
~~~~~~

.. code-block:: python

   In [1]: %load_ext memory_profiler
   In [2]: from app import Request
   In [3]: %memit Request({})
   peak memory: 36.04 MiB, increment: 0.01 MiB

   In [4]: %memit [Request({}) for n in range(10000)]
   peak memory: 41.63 MiB, increment: 5.52 MiB

10000個作った時のメモリ使用量は 5.52MiB でした。


After
~~~~~

.. code-block::

   In [1]: %load_ext memory_profiler
   In [2]: import app
   In [3]: import importlib
   In [4]: importlib.reload(app)
   Out[4]: <module 'app' from '/Users/c-bata/PycharmProjects/developing-web-framework/app.py'>
   In [5]: r = app.Request({})
   In [6]: r.a = 1
   ---------------------------------------------------------------------------
   AttributeError                            Traceback (most recent call last)
   <ipython-input-16-51d02eb8a4fe> in <module>()
   ----> 1 r.a = 1

   AttributeError: 'Request' object has no attribute 'a'

   In [7]: %memit [app.Request({'foo': 'bar'}) for i in range(100000)]
   peak memory: 68.89 MiB, increment: 18.57 MiB

   In [8]: importlib.reload(app)
   Out[8]: <module 'app' from '/Users/c-bata/PycharmProjects/developing-web-framework/app.py'>
   In [9]: r = app.Request({})
   In [10]: r.a = 1
   In [11]: %memit [app.Request({'foo': 'bar'}) for i in range(100000)]
   peak memory: 76.14 MiB, increment: 25.55 MiB

reloadする前は、 `__slots__` が定義されており、メモリ使用量は18.57MiB
reloadした後は、 `__slots__` が定義されておらず、メモリ使用量は25.55MiB
節約できていることが確認できる。
