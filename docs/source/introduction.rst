はじめに
====

筆者は自分の一番の強みをサーバサイドにしようと考えた時に、DjangoやFlaskなど主要なWebフレームワークの実装を
知っておきたいと考えるようになりました。
バグにぶつかった時に、自分では修正できないから誰かが修正してくれるのを待つだけっていうのは、出来るだけやめていきたい。
自分で問題を修正できる技術をつけたいと考え、BottleやFlaskのソースコードリーディングを始めました。
色々な実装が分からず、つまづきながらも多くの知識をみにつけることができました。

フレームワークの勉強に一番いいのは、自分で実装することだと考えています。
この資料では200行に満たないシンプルなWebフレームワークの作り方について解説します。

みなさんには、この資料を読んでBottleやKobinのソースコードをまず読んでみて欲しいと考えています。


対象読者
----

この資料では実際にPythonでWebアプリケーションのフレームワークを作っていきます。
そのため、FlaskやBottle、Djangoなどのフレームワークを使ってアプリケーションを開発したことがあると理解がしやすいかと思います。
またHTTPの知識があると理解がしやすいかもしれません。

もし読み進めていく中で難しいと感じた場合は、これらの知識をもう少し復習してみるといいかもしれません。
どうしてもわからない場合はGithubの方にIssueをたてていただけると、そのあたりの補足説明を増やせるかもしれません。
お気軽に連絡ください。


本資料に必要なもの
---------

本資料では下記の環境で解説を進めています。

- Python 3.5.2


作成するフレームワークの概要
--------------

この資料で作成するフレームワークを使うと次のようにコードを記述出来ます。

.. code-block:: python

   from app import App, Response, JSONResponse
   from wsgiref.simple_server import make_server

   app = App(__name__)


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


.. todo:: 実際に作ったTodoアプリケーションの動作の様子はこちらです。
