ルーティング
============

シンプルなルーティング
----------------------

前章では、WSGIの仕様について確認し、それを満たす小さなアプリケーションをつくりました。
ここからは実際にWebフレームワークを作っていきましょう。

先程のアプリケーションでは、URLのパス情報によらず全て「Hello World」と返しています。
実際のアプリケーションでは、沢山のページが存在するためパス情報に応じてそれぞれ違ったレスポンスを返す必要があります。
最も簡単なルーティング方法を次に示します。

.. code-block:: python

    def application(env, start_response):
        path = env['PATH_INFO']
        if path == '/':
            start_response('200 OK', [('Content-type', 'text/plain')])
            return [b'Hello World']
        elif path == '/foo':
            start_response('200 OK', [('Content-type', 'text/plain')])
            return [b'foo']
        else:
            start_response('404 Not Found', [('Content-type', 'text/plain')])
            return [b'404 Not Found']

WSGIのアプリケーションの第一引数には、辞書型オブジェクトが渡されています。
これは WSGI Environment と呼ばれ、クライアントから受け取ったリクエストの情報が格納されています。
リクエストのパス情報もその一つで、 `PATH_INFO` により取り出すことができます。
またHTTPのメソッドも同様に ``REQUEST_METHOD`` により取り出すことができます。


URL変数と正規表現によるルーティング
-----------------------------------

URL変数
~~~~~~~

もう少し複雑なケースを考えてみましょう。
こちらのBottleのアプリケーションの一部を見てください。

.. code-block:: python

   @route('/hello/<name>')
   def greet(name='Stranger'):
       return template('Hello {{name}}, how are you?', name=name)

   @route('/users/<user_id:int>')
   def user_detail(user_id):
       users = ['user{id}'.format(id=i) for i in range(10)]
       return template('Hello {{user}}', user=users[user_id])

`/hello/foo` と `/hello/bar` はそれぞれ別のエンドポイントですが、上のコードではどちらも `greet` 関数が呼ばれます。
またURLのパス情報から `foo` や `bar` などの変数(以下、URL変数)を取り出しています。

先程のようにif文で分岐させていくのは大変なので、別の方法を考えてみましょう。
解決策の一つとして正規表現の利用があります。


正規表現モジュール
~~~~~~~~~~~~~~~~~~

`正規表現 <http://docs.python.jp/3/library/re.html>`_ は普段使わない方も多いかと思います。
ここで簡単におさらいしましょう。

.. code-block:: python

   >>> import re
   >>> url_scheme = '/users/(?P<user_id>\d+)/'
   >>> re.match('/users/(?P<user_id>\d+)/', '/users/1/').groupdict()
   {'user_id': '1'}

   >>> pattern = re.compile(url_scheme)
   >>> pattern.match('/users/1/').groupdict()
   {'user_id': '1'}

このように名前付きグループでパターンを定義し、マッチするか確認してからgroupdictを呼ぶことでuser_idの部分の数字が文字列で取得出来ます。


構成図
~~~~~~

それでは、ルーティング機能を提供するため、フレームワークの実装を始めましょう。
ここで提供するルーティングは次のようなイメージです。

.. figure:: _static/structure/router.png
   :width: 300px
   :align: center
   :alt: ルーティングのイメージ

   ルーティングのイメージ。
   パス情報にあわせて別のアプリケーションを呼び出す。

それでは図のRouterを実装していきましょう。


Routerクラス
------------

それではルーティングの機能を提供する ``Router`` クラスを用意していきます。
このクラスには2つのメソッドを用意します。

1. ``add()``: 各コールバック関数(WSGIアプリケーションオブジェクト)が、どのURLパス・HTTPメソッドに紐づくかを登録する。
2. ``match()``: 実際に受け取ったリクエストのパスとHTTPメソッドの情報を元に登録していたコールバック関数とURL変数を返す。

まずは ``add()`` メソッドから定義してみましょう。

.. code-block:: python

   class Router:
       def __init__(self):
           self.routes = []

       def add(self, method, path, callback):
           self.routes.append({
               'method': method,
               'path': path,
               'callback': callback
           })

HTTPメソッドとパス、それに紐づくコールバック関数を辞書型のオブジェクトにつめて、リストに追加しました。
非常に簡単です。呼び出し側はどのようになるでしょうか？ ``match()`` メソッドを定義します。

.. code-block:: python

   import re


   def http404(env, start_response):
       start_response('404 Not Found', [('Content-type', 'text/plain; charset=utf-8')])
       return [b'404 Not Found']


   class Router:
       ...

       def match(self, method, path):
           for r in self.routes:
               matched = re.compile(r['path']).match(path)
               if matched and r['method'] == method:
                   url_vars = matched.groupdict()
                   return r['callback'], url_vars
           return http404, {}


このメソッドでは、 ``add()`` メソッドで登録したエンドポイントのパス情報とメソッド情報が一致するかをチェックします。
もし一致した場合には、URL変数を取り出し、ひも付けられていたコールバック関数を返します。
一致しない場合には、 ``404 Not Found`` を返すようになりました。
こちらも非常にシンプルなコードですが、基本的にルーティングに必要な機能を備えています。
念の為動作も確認しましょう。

.. code-block:: python

   >>> from app import Router
   >>> router = Router()

   # コールバック関数の定義
   >>> def create_user():
   ...     return 'user is created'
   ...
   >>> def user_detail(id):
   ...     return 'user{id} detail'.format(id)
   ...

   # エンドポイントの登録
   >>> router.add('POST', '^/users/$', create_user)
   >>> router.add('GET', '^/users/(?P<user_id>\d+)/$', user_detail)

   # 呼び出し確認
   >>> callback, kwargs = router.match('POST', '/users/')
   >>> callback(**kwargs)
   'user is created'
   >>> callback, kwargs = router.match('GET', '/users/1/')
   >>> callback(**kwargs)
   'user1 detail'

   # 定義されていないエンドポイントでは次のように http404 関数が callback として返ってきます。
   >>> callback, kwargs = r.match('POST', '/foobar')
   >>> callback
   <function http404 at 0x103696840>
   >>> dummy_start_response = lambda x, y: print(x, y)
   >>> callback({}, dummy_start_response, **kwargs)
   404 Not Found [('Content-type', 'text/plain; charset=utf-8')]
   [b'404 Not Found']


うまく動作していることが確認できます。
ここではついでに2つ改善を加えておきましょう。

1. パスは定義されているもののメソッドだけが一致しない場合には ``405 Method Not Allowed`` を返す。
2. ``re.compile()`` は ``Router.add()`` メソッドの呼び出し時に行っておく。

修正を加えると全体像は次のようになります。

.. code-block:: python

   import re


   def http404(env, start_response):
       start_response('404 Not Found', [('Content-type', 'text/plain; charset=utf-8')])
       return [b'404 Not Found']


   def http405(env, start_response):
       start_response('405 Method Not Allowed', [('Content-type', 'text/plain; charset=utf-8')])
       return [b'405 Method Not Allowed']


   class Router:
       def __init__(self):
           self.routes = []

       def add(self, method, path, callback):
           self.routes.append({
               'method': method,
               'path': path,
               'path_compiled': re.compile(path),
               'callback': callback
           })

       def match(self, method, path):
           error_callback = http404
           for r in self.routes:
               matched = r['path_compiled'].match(path)
               if not matched:
                   continue

               error_callback = http405
               url_vars = matched.groupdict()
               if method == r['method']:
                   return r['callback'], url_vars
           return error_callback, {}


他にもいろいろと考えることはありますが、今はこれくらいにしておきます。
それでは ``Router`` クラスを実際にアプリケーションに組み込んでいきます。


Routerを組み込んだWSGIのアプリケーション用クラスを作る
------------------------------------------------------

``Router`` クラスを組み込んで行きたいのですが、関数のままだと少し扱いづらいです。
ここではWSGIアプリケーションをクラスで定義してみましょう。

.. code-block:: python

   class App:
       def __call__(self, env, start_response):
           start_response('200 OK', [('Content-type', 'text/plain')])
           return [b'Hello World']

ここで注目してほしいのは ``__call__()`` メソッドが定義されている点です。
``__call__`` メソッドを定義すると、このクラスのオブジェクト自身が呼び出し可能(callable)になります。
つまり ``app = App()`` は、関数 ``def app(env, start_response): pass`` 同じように振る舞ってくれます。
これでだいぶ拡張がしやすくなりました。 ``Router`` クラスを組み込んでみましょう。

.. code-block:: python

   class App:
       def __init__(self):
           self.router = Router()

       def route(self, path=None, method='GET', callback=None):
           def decorator(callback_func):
               self.router.add(method, path, callback_func)
               return callback_func
           return decorator(callback) if callback else decorator

       def __call__(self, env, start_response):
           method = env['REQUEST_METHOD'].upper()
           path = env['PATH_INFO'] or '/'
           callback, kwargs = self.router.match(method, path)
           return callback(env, start_response, **kwargs)


``route`` デコレーターを使ってコールバック関数にHTTPメソッドと正規表現で書かれたパスを割り当てできるようにしました。
このフレームワークの利用者からは、次のような形で利用出来ます。

.. literalinclude:: _codes/routing/main.py

実際にアプリケーションを実行して動作確認してみましょう。
定義されたエンドポイントにアクセスすると、次のように正しくレスポンスを受け取ることができます。

.. code-block:: console

   $ curl http://127.0.0.1:8000/
   Hello World
   $ curl -X POST http://127.0.0.1:8000/user/
   User Created
   $ curl http://127.0.0.1:8000/user/shibata/
   Hello shibata
   $ curl -X POST http://127.0.0.1:8000/user/shibata/follow/
   Followed shibata

一方で定義されていないパスや、メソッドが定義されていないエンドポイントでは、404 や 405が返ってきます。

.. code-block:: console

   $ curl http://127.0.0.1:8000/foobar
   404 Not Found
   $ curl http://127.0.0.1:8000/user/shibata/follow/
   405 Method Not Allowed


まとめ
------

ここまでルーティングの役割について考え、実装しました。
用意した ``Router`` クラスは、正規表現で記述されたパスにマッチするかどうかを判定し、
マッチした場合には登録しておいたコールバック関数とURL変数を返してくれます。
デコレーターでルーティングの情報を指定することで、ユーザーは複数のエンドポイントを見通しよく定義できるようになりました。

.. ここでは reverse routing とか traversal routing を扱わない

..
.. 逆引き(Reversing)に対応する
.. -------------------
..
.. 逆引きに対応しましょう。
.. 正規表現ベースのルーティングはその自由度の高さと引き換えに、逆引きが困難になっています。
.. 今回は正規表現ではなく、次のような形式で記述してみましょう。
..
.. .. code-block:: python
..
..    @app.route('/users/{id})
..    def user_detail(id: int):
..        return 'Hello user{id}'.format(id=id)
..
.. `/users/{id}` の形式であれば逆引きは以下のように簡単に出来ます.

.. .. code-block:: python
..
..    >>> url = '/users/{id}/'
..    >>> url.format(id=1)
..    '/users/1/'

.. formatメソッドにより逆引きが非常に容易になりました


.. 正引きの方法
.. ~~~~~~
..
.. 整備機は少し複雑です。
..
.. 1. '/users/{id}/' を '/' で分割.
.. 2. requestのpath情報も同じように '/' で分割し、長さを比較
..     - 一致すれば次に進む
..     - 一致しなければ、このURLではないと判断
.. 3. 前から順番に文字列を比較.
..     - '{' で開始して '}' で終了するときは、TypeHintsの情報にキャストできるかどうかチェック
.. 4. 全て一致する、もしくはキャスト可能であればOK


.. TraversalとURL Dispatch
.. ----------------------
..
.. これまで説明してきた方法は、URL Dispatchとよばれるものです。
.. 各URLのパターンをリストのように持ち、一致するかどうかそれぞれチェックしていました。
.. 他の方法として親子関係によりURLの構造を表現するTravarsalと呼ばれるものがあります。
.. URL Dispatchの方が比較的よく利用されますが、Pyramidはどちらも指定できるようになっています。
..
.. 興味のある方は下記の記事を読んでみてください
..
.. http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/hybrid.html
