Webフレームワークの構造
=============

フレームワークに求められる機能とは？
------------------

Hello Worldを表示するだけの簡単なアプリケーションであれば、フレームワークを使わずに実装することが出来ました。
それではこれからWebアプリケーションを開発する上で、Webフレームワークがどのような機能を提供すると楽になるでしょうか。

ルーティング
~~~~~~

先ほどのHello WorldのアプリケーションはどこにアクセスしてもHello Worldが返ってきます。


リクエストオブジェクト・レスポンスオブジェクト
~~~~~~~~~~~~~~~~~~~~~~~

リクエスト情報は、WSGIアプリケーションの第一引数として提供されますが、こちらは辞書型のオブジェクトです。
ここから直接、GETのクエリパラメータやその他のリクエスト情報を取り出すのは大変なため、
それらの情報をうまくラップしてくれるクラスがあるといいでしょう。

またレスポンスのヘッダ情報やステータス情報もうまく管理してくれるクラスがあるとよさそうです。


HTMLテンプレート
~~~~~~~~~~

HTMLを表示する際に、Pythonの変数を評価して埋め込めると便利です。
BottleやDjangoのように、自前でテンプレートエンジンを用意してもいいかもしれませんが、Jinja2などすでに
広く利用されているテンプレートエンジンのローダがあると便利かもしれません。

今回は一から実装はせずに、Jinja2のテンプレートエンジンのローダを用意します。


静的ファイルの配信
~~~~~~~~~

CSSやJS、画像ファイルなどの静的ファイルは、本番環境の場合、 Nginx 等で返す場合が多いかもしれません。
しかし開発中や手元のパソコンでも Nginx の設定をして静的ファイルを返すように設定するのは面倒なので、
フレームワークにも静的ファイルを返す機能があると開発が捗りそうです。


今回作成するWebフレームワーク
----------------

この資料で作成するフレームワークを使うと次のようにコードを記述出来ます。

.. code-block:: python

   from app import App, Response, JSONResponse
   from wsgiref.simple_server import make_server

   app = App()


   @app.route('^/$')
   def index(request):
       return Response('Hello World')


   @app.route('^/users/(?P<user_id>\d+)/$')
   def user_detail(request, user_id):
       data = {'user': user_id}
       return JSONResponse(data, indent=4)

   if __name__ == '__main__':
       httpd = make_server('', 8000, app)
       httpd.serve_forever()

フレームワークの全体像
-----------

フレームワークの全体像は次のようになっています。


.. figure:: _static/structure/middleware.png
   :width: 400px
   :align: center
   :alt: フレームワークの全体像

   フレームワークの全体像
