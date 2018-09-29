レスポンスオブジェクト
======================

レスポンス情報の扱いについて
----------------------------------------

一度、各エンドポイントの処理の定義方法を見直してみましょう。

.. code-block:: python

   @app.route('^/$', 'GET')
   def hello(request, start_response):
       start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
       return [b'Hello World']

ここで気になるのは、レスポンス情報の返し方です。
WSGIのインターフェイスでは、レスポンスステータスとレスポンスヘッダーを第2引数で受け取る ``start_response`` 関数により指定します。
これはFlaskやBottleのサンプルコードに比べると、少々面倒に感じます。
もう少し簡単に管理できるように、Response情報をラップするクラスがあると便利かもしれません。
具体的には次のように各エンドポイントの処理を記述できるようにしてみます。

.. code-block:: python

   @app.route('^/$', 'GET')
   def hello(request):
       return Response('Hello World')

   @app.route('^/user/$', 'POST')
   def create_user(request):
       return Response('User is created', headers={"foo": "bar"}, status=201)

Responseクラスというのを追加して、レスポンスボディやヘッダー情報、ステータスコードの番号をそこに指定できるようにしました。
クラスでラップしているので、デフォルトのヘッダー情報も継承を使って自由に変更することもできます。


ヘッダー情報とステータス情報を簡単に扱う方法
--------------------------------------------

Responseクラスを実装していく前に、ヘッダー情報とステータス情報を簡単に扱う方法を詳解します。
まずはステータス情報の扱いです。 ``start_response`` の第一引数にはステータスコードを ``200 OK`` や ``404 Not Found`` のように指定しますが、
番号に対応する文字列は決まっているので、番号の指定だけで済むほうが楽なものです。
``http.client`` モジュールの ``responses`` オブジェクトには、ステータスコードの番号に対するメッセージが格納されています。

.. code-block:: python

   >>> from http.client import responses
   >>> responses[200]
   'OK'
   >>> responses[404]
   'Not Found'
   >>> responses[500]
   'Internal Server Error'

非常に簡単に取り出すことができました。ユーザーは ``200`` のように番号を指定してあげるだけで、次のようにステータスコードを生成できます。

.. code-block:: python

   >>> from http.client import responses
   >>> def get_status_code(number):
   ...     return f"{number} {responses[number]}"
   ...
   >>> get_status_code(200)
   '200 OK'
   >>> get_status_code(400)
   '400 Bad Request'

ステータス情報の管理には ``wsgiref.headers`` モジュールの中にある ``Header`` クラスが便利です。

.. code-block:: python

   >>> from wsgiref.headers import Headers
   >>> h = Headers()
   >>> h.add_header('Content-type', 'text/plain')
   >>> h.add_header('Foo', 'bar')
   >>> h.items()
   [('Content-type', 'text/plain'), ('Foo', 'bar')]

``add_header(key, value)`` メソッドをとおして、ヘッダー情報をセットします。
またWSGIの仕様上、ヘッダー情報をキーとバリューのタプルのリストを用意する必要がありますが、
``items()`` メソッドはその形式でヘッダー情報を吐き出してくれます。


Responseクラスを用意して組み込む
----------------------------------------

レスポンスクラスは次のようになります。

.. code-block:: python

   from http.client import responses as http_responses
   from wsgiref.headers import Headers

   class Response:
       default_status = 200
       default_charset = 'utf-8'
       default_content_type = 'text/html; charset=UTF-8'

       def __init__(self, body='', status=None, headers=None, charset=None):
           self._body = body
           self.status = status or self.default_status
           self.headers = Headers()
           self.charset = charset or self.default_charset

           if headers:
               for name, value in headers.items():
                   self.headers.add_header(name, value)

       @property
       def status_code(self):
           return "%d %s" % (self.status, http_responses[self.status])

       @property
       def header_list(self):
           if 'Content-Type' not in self.headers:
               self.headers.add_header('Content-Type', self.default_content_type)
           return self.headers.items()

       @property
       def body(self):
           if isinstance(self._body, str):
               return [self._body.encode(self.charset)]
           return [self._body]

デフォルトのステータスコードやコンテントタイプをクラス変数にもたせておくことにしました。
ユーザーはレスポンスボディの内容を文字列で指定していますが、WSGIのインターフェイスではバイト文字列を yield するイテラブルなオブジェクトとして返さなくてはいけません。
``body`` プロパティメソッドが適切に文字列をエンコードして返してくれます。

アプリケーションにも組み込んでみましょう。

.. code-block:: python

   class App:
       ...

       def __call__(self, env, start_response):
           request = Request(env)
           callback, url_vars = self.router.match(request.method, request.path)

           response = callback(request, **url_vars)
           start_response(response.status_code, response.header_list)
           return response.body

組み込みはこのように非常に簡単です。これまでとは違い ``start_response`` を各関数に渡す必要はありません。
そのかわり返ってきたレスポンスオブジェクトから、ステータス情報とヘッダー情報を取り出して呼び出して上げる必要があります。

こうするとユーザーの定義する関数は驚くほどシンプルになります。
具体的には、次のようになりました。

.. literalinclude:: _codes/response/main.py

いかがでしょう、FlaskやBottleを使ったことのある方には随分と見慣れた形になってきたのではないでしょうか。


まとめ
-------

ここではレスポンス情報の扱いを見直しました。
Responseクラスを追加することで随分ユーザーにとって使いやすいAPIに変えることができました。
実際にアプリケーションを作っていくにはまだまだ欲しい機能がありますが、ここまでくればまさにWebフレームワークと言えるものになってきたのではないでしょうか。

ここでは全部文字列をただ返していましたが、実際のユースケースではHTMLやJSONを返すことが多いでしょう。
その内容は次の節で扱っていきます。


.. チューニング
.. ------
..
.. RequestやResponseのクラスはリクエストがある度に、生成されているためパフォーマンスに大きく影響していそうです。
.. ここでは `__slots__` 属性を用いることでメモリを大幅に節約することが出来ます。
.. 試してみましょう。
..
..
.. Before
.. ~~~~~~
..
.. .. code-block:: python
..
..    In [1]: %load_ext memory_profiler
..    In [2]: from app import Request
..    In [3]: %memit Request({})
..    peak memory: 36.04 MiB, increment: 0.01 MiB
..
..    In [4]: %memit [Request({}) for n in range(10000)]
..    peak memory: 41.63 MiB, increment: 5.52 MiB
..
.. 10000個作った時のメモリ使用量は 5.52MiB でした。
..
..
.. After
.. ~~~~~
..
.. .. code-block:: python
..
..    In [1]: %load_ext memory_profiler
..    In [2]: import app
..    In [3]: import importlib
..    In [4]: importlib.reload(app)
..    Out[4]: <module 'app' from '/Users/c-bata/PycharmProjects/developing-web-framework/app.py'>
..    In [5]: r = app.Request({})
..    In [6]: r.a = 1
..    ---------------------------------------------------------------------------
..    AttributeError                            Traceback (most recent call last)
..    <ipython-input-16-51d02eb8a4fe> in <module>()
..    ----> 1 r.a = 1
..
..    AttributeError: 'Request' object has no attribute 'a'
..
..    In [7]: %memit [app.Request({'foo': 'bar'}) for i in range(100000)]
..    peak memory: 68.89 MiB, increment: 18.57 MiB
..
..    In [8]: importlib.reload(app)
..    Out[8]: <module 'app' from '/Users/c-bata/PycharmProjects/developing-web-framework/app.py'>
..    In [9]: r = app.Request({})
..    In [10]: r.a = 1
..    In [11]: %memit [app.Request({'foo': 'bar'}) for i in range(100000)]
..    peak memory: 76.14 MiB, increment: 25.55 MiB
..
.. reloadする前は、 `__slots__` が定義されており、メモリ使用量は18.57MiB
.. reloadした後は、 `__slots__` が定義されておらず、メモリ使用量は25.55MiB
.. 節約できていることが確認できる。
