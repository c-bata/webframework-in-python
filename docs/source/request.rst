リクエストオブジェクト
======================

リクエストに関する情報の扱いについて
----------------------------------------

次はリクエスト情報の扱い方について考えてみましょう。
クライアントのリクエストに関する情報はWSGIアプリケーションの第一引数に辞書型のオブジェクトとして渡されることはすでに解説しました。
ルーティングに必要なリクエストのHTTPメソッドやURLパスは、次のようにこのオブジェクトから取り出す必要があります。

.. code-block:: python

   method = env['REQUEST_METHOD'].upper()
   path = env['PATH_INFO']

また他にも様々な情報が格納されていて、例えばHTTPリクエストボディを取り出したい際には、次のように記述します。

.. code-block:: python

   content_length = int(env.get('CONTENT_LENGTH', 0))
   body = env['wsgi.input'].read(content_length)

辞書型オブジェクトから ``CONTENT_LENGTH`` と ``wsgi.input`` を取り出します。
``env["CONTENT_LENGTH"]`` には、クライアントがHTTPヘッダー ``Content-Length`` で指定したレスポンスボディの長さが格納されています。
レスポンスボディはファイルオブジェクトになっているので、 ``Content-Length`` の長さ分 ``read()`` して上げる必要があります。
リクエストボディを取り出すだけでも少し大変なように思います。

これらをうまくラップして使いやすくしてくれるクラスがあれば便利です。
ほとんどのWSGIフレームワークがこれをラップする ``Request`` クラスや ``HttpRequest`` クラスを提供します。
このフレームワークにも同様に定義してみましょう。


WSGI Environオブジェクトをラップする
------------------------------------

厳密にはWSGIのEnvironをラップします。
プロパティメソッドを通して、WSGI Environに格納されている様々な情報にシンプルなAPIでアクセスできるようにします。

.. code-block:: python

   class Request:
       def __init__(self, environ):
           self.environ = environ
           self._body = None

       @property
       def path(self):
           return self.environ['PATH_INFO'] or '/'

       @property
       def method(self):
           return self.environ['REQUEST_METHOD'].upper()

       @property
       def body(self):
           if self._body is None:
               content_length = int(self.environ.get('CONTENT_LENGTH', 0))
               self._body = self.environ['wsgi.input'].read(content_length)
           return self._body

WSGI Environには様々な情報が格納されていますが、まずは3つだけプロパティメソッドを定義してみました。
この ``Request`` クラスのオブジェクトを渡してあげれば、フレームワークの利用者は ``body`` プロパティにアクセスするだけで、リクエストボディの情報を取得できます。
実際にはここであげた他にもたくさんの情報が詰まっているので、必要に応じて拡張していく必要がありますが基本的な考え方はこれだけです。
次はアプリケーションに組み込んでみましょう。


アプリケーションに組み込む
------------------------------------

各関数には、WSGI Environの代わりに ``Request(env)`` を渡すように書き換えてみましょう。

.. code-block:: python

   class App:
       ...

       def __call__(self, env, start_response):
           request = Request(env)
           callback, kwargs = self.router.match(request.method, request.path)
           return callback(request, start_response, **kwargs)


これで ``Request`` クラスのオブジェクトが各関数に渡せるようになりました。
アプリケーション側のインターフェイスは次のようになります。

.. code-block:: python

   @app.route('^/users/$', 'POST')
   def hello(request, start_response):
       print(request.body.decode('utf-8'))
       return [b'User is created']

リクエストボディの文字コードをすべて ``utf-8`` として扱っている点には改善の余地があります。
実際には ``Content-Type`` ヘッダーなどで指定されている ``charset`` を確認してあげるといいでしょう。
とはいえひとまず、フレームワークの利用者は簡単にリクエストボディにアクセスできるようになりました。
既存のアプリケーションを書き換えてみます。


.. literalinclude:: _codes/request/main.py


リクエストオブジェクトを拡張していく
------------------------------------

せっかくなのでもう少し他の情報にアクセスできるようにしておきましょう。
WSGI Environに入っているすべての情報をラップすることはここではしませんが、次に挙げる項目は利用頻度が高いため、プロパティメソッドが定義されていると便利かと思います。

* `query` プロパティ: URLのクエリパラメーターを手軽に取り出したい
    * ``env['QUERY_STRING']`` より取り出して ``urllib.parse.parse_qs`` を用いてパースできます
* `forms` プロパティ: ``form-urlencoded`` 形式や ``multipart`` 形式で格納されているHTMLフォーム等から送られたパラメーターを受け取りたい。
    * リクエストボディから取り出して、 ``cgi.FieldStorage`` を用いてパースできます。
* `text` プロパティ: リクエストボディをバイト列ではなくテキストで受け取りたい。
* `json` プロパティ: リクエストボディの内容をjson decodeして、辞書型オブジェクトとして受け取りたい。

コードはそれほど難しくないので細かい説明は省きますが、プロパティメソッドは次のようになります。

.. code-block:: python

   import cgi
   import json
   from urllib.parse import parse_qs, urljoin

   class Request:
       def __init__(self, environ, charset='utf-8'):
           self.environ = environ
           self._body = None
           self.charset = charset

       @property
       def path(self):
           return self.environ['PATH_INFO'] or '/'

       @property
       def method(self):
           return self.environ['REQUEST_METHOD'].upper()

       @property
       def forms(self):
           form = cgi.FieldStorage(
               fp=self.environ['wsgi.input'],
               environ=self.environ,
               keep_blank_values=True,
           )
           params = {k: form[k].value for k in form}
           return params

       @property
       def query(self):
           return parse_qs(self.environ['QUERY_STRING'])

       @property
       def body(self):
           if self._body is None:
               content_length = int(self.environ.get('CONTENT_LENGTH', 0))
               self._body = self.environ['wsgi.input'].read(content_length)
           return self._body

       @property
       def text(self):
           return self.body.decode(self.charset)

       @property
       def json(self):
           return json.loads(self.body)


まとめ
-------------------

ここではリクエストオブジェクトの扱いについて見直していきました。
WSGI Environではそのままではリクエスト情報の取り出しが少し面倒でしたが、
それをラップするリクエストクラスを用意することで、プロパティメソッドを通して
様々な情報を手軽に取り出せる様になりました。
リクエストの次はレスポンス情報を扱いやすいAPIになおしていきましょう。


.. URLのクエリーパラメーターを手軽に取り出す
.. ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
..
.. URLのクエリパラメーターは ``env['QUERY_STRING']`` により取得できます。
.. ここには `foo=bar&hoge=fuga`` の形式で格納されているため別途パースして上げる必要があります。
..
.. .. code-block:: python
..
..    >>> from urllib.parse import parse_qs
..    >>> parse_qs('foo=bar&hoge=fuga')
..    {'hoge': ['fuga'], 'foo': ['bar']}
..
.. これを組み込むと次のようになります。


