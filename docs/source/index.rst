================================
Webアプリケーションフレームワークの作り方 in Python
================================

こんにちは、芝田 将 (@c_bata_) です。
この資料はPyCon JP 2016で行った `「基礎から学ぶWebアプリケーションフレームワークの作り方」 <https://pycon.jp/2016/ja/schedule/presentation/14/>`_ の補足資料です。

誤字等があれば、Githubの方にIssue or PRをお待ちしております。

`c-bata/WebFramework-in-Python - Github <https://github.com/c-bata/webframework-in-python>`_


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


この資料のゴール
========

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


目次
====

.. toctree::
   :maxdepth: 2

   wsgi
   structure
   routing
   environ
   template
   middleware
   kobin


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
