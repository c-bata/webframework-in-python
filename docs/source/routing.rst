ルーティング
======

ルーティング時のパス情報の指定方法にはいくつか方法があります。

- Djangoのような正規表現ベースのルーティング
- Flaskのような独自の指定方法によるルーティング


シンプルなルーティング
-----------

まずはフレームワーク側ではなく、ユーザ側でルーティングを実装してみましょう。

WSGIのアプリケーションの第一引数(以下、env)にはリクエストに関する様々な情報が含まれています。
ユーザのアクセスしようとしているPathの情報もその1つです。
次のコードを見てください。

.. code-block:: python

    def application(env, start_response):
        path = env['PATH_INFO']
        if path == '/foo':
            return [b'foo']
        return [b'Hello World']

その最もシンプルなルーティングはこのようになるでしょう。


正規表現ベースのルーティング
--------------

ここでは正規表現ベースのルーティングを実装しましょう。
ルーティングにはいくつか欲しい機能があります。

- `/users/<user_id/` のような動的なURL上での値(URL Vars)を受け取りたい.


Pythonの正規表現モジュール
~~~~~~~~~~~~~~~~

まずは `正規表現 <http://docs.python.jp/3/library/re.html>`_ について簡単に復習します。

.. code-block:: python

   >>> import re
   >>> url_scheme = '/users/(?P<user_id>\d+)/'
   >>> pattern = re.compile(url_scheme)
   >>> pattern.match('/users/1/').groupdict()
   {'user_id': '1'}

このように名前付きグループでパターンを定義し、マッチするか確認してからgroupdictを呼ぶことでuser_idの部分の数字が文字列で取得出来ます。


Routerクラス
~~~~~~~~~

Routerクラスを用意します。

1. add メソッドにより、各ルートの情報を辞書型オブジェクトのリストに格納する
2. matchするか調べる

.. code-block:: python

   import re


   class Router:
       def __init__(self):
           self.routes = []

       def add(self, method, path, callback):
           self.routes.append({
               'method': method,
               'path': path,
               'callback': callback
           })

       def match(self, method, path):
           for r in filter(lambda x: x['method'] == method.lower(), self.routes):
               matched = re.compile(r['path']).match(path)
            if matched:
                kwargs = matched.groupdict()
                return r, kwargs
        return b'404 Not Found'


試しに動作確認

.. code-block:: python

   >>> from routes import Router
   >>> router = Router()
   >>> def users():
   ...     return 'user list'
   >>> def create_user():
   ...     return 'create user'
   >>> def user_detail(id):
   ...     return 'user{id} detail'.format(id)
   >>> router.add('get', '^/users/$', users)
   >>> router.add('post', '^/users/$', create_user)
   >>> router.add('get', '^/users/(?P<user_id>\d+)/$', user_detail)
   >>> route, kwargs = router.match('get', '/users/')
   >>> route['callback'](**kwargs)
   'user list'
   >>> route, kwargs = router.match('post', '/users/')
   >>> route['callback'](**kwargs)
   'create user'
   >>> route, kwargs = router.match('get', '/users/1/')
   >>> route['callback'](**kwargs)
   'user1 detail'

うまく機能していますね。


最終的なコードはこちらです。

.. literalinclude:: _codes/routing.py


逆引き(Reversing)に対応する
-------------------

逆引きに対応しましょう。
正規表現ベースのルーティングはその自由度の高さと引き換えに、逆引きが困難になっています。
今回は正規表現ではなく、次のような形式で記述してみましょう。

.. code-block:: python

   @app.route('/users/{id})
   def user_detail(id: int):
       return 'Hello user{id}'.format(id=id)

`/users/{id}` の形式であれば逆引きは以下のように簡単に出来ます.

.. code-block:: python

   >>> url = '/users/{id}/'
   >>> url.format(id=1)
   '/users/1/'

formatメソッドにより逆引きが非常に容易になりました


正引きの方法
~~~~~~

整備機は少し複雑です。

1. '/users/{id}/' を '/' で分割.
2. requestのpath情報も同じように '/' で分割し、長さを比較
    - 一致すれば次に進む
    - 一致しなければ、このURLではないと判断
3. 前から順番に文字列を比較.
    - '{' で開始して '}' で終了するときは、TypeHintsの情報にキャストできるかどうかチェック
4. 全て一致する、もしくはキャスト可能であればOK


正引きの方法
~~~~~~

.. todo:: 正引きの仕方

.. note::

   ルーティングの実装時に考えていたことを、いくつかブログにまとめています。
   興味のある方は読んでみてください :)

   `Python製WebフレームワークのURL DispatcherとType Hintsの活用について | c-bata web <http://nwpct1.hatenablog.com/entry/url-dispatcher-with-type-hints-in-python>`_


TraversalとURL Dispatch
----------------------

これまで説明してきた方法は、URL Dispatchとよばれるものです。
各URLのパターンをリストのように持ち、一致するかどうかそれぞれチェックしていました。
他の方法として親子関係によりURLの構造を表現するTravarsalと呼ばれるものがあります。
URL Dispatchの方が比較的よく利用されますが、Pyramidはどちらも指定できるようになっています。

興味のある方は下記の記事を読んでみてください

http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/hybrid.html
