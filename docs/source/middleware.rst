WSGIミドルウェア
==========

ミドルウェアとは
--------

次はJavaScriptやCSS、画像などの静的ファイルを返す機能をつけてみましょう。
本番環境では、パフォーマンスの観点からNginx等で直接返すことが多いかもしれませんが、
開発環境でもNginxなどの設定をしておくのは、かなり面倒です。

静的ファイルを返す機能をどのように追加するか、いくつか方法はありますが今回はWSGIのミドルウェアとして実装してみます。

ミドルウェアは、Webサーバ側からはWSGIアプリケーションのように見えWSGIアプリケーション側からはWebサーバのように見えます。

.. code-block:: python

   class SomeMiddleware:
       def __init__(self, app):
           self.app = app

       def __call__(self, env, start_response):
        return self.app(env, start_response)


静的ファイルの配信
---------

CSSやJS、画像などの静的ファイルの配信は、本番環境ではNginx等で返すことが多いかと思います。
しかし開発中にNginx等で返すように設定するのは面倒です。

開発環境でのみ、静的ファイルを配信するミドルウェアを有効化してみましょう。
静的ファイルの配信方法の実装については、ここでは割愛します。
既に公開されている静的ファイルを返すミドルウェアは古いものが多かったので筆者の方で用意しました。

`wsgi-static-middleware <https://pypi.python.org/pypi/wsgi-static-middleware>`_

この wsgi-static-middleware を使って静的ファイルを有効にしてみましょう。

.. code-block:: python

   from app import App, Response
   from wsgi_static_middleware import StaticMiddleware

   BASE_DIR = os.path.dirname(__name__)
   STATIC_DIRS = [os.path.join(BASE_DIR, 'static')]

   app = App()


   @app.route('^/$')
   def index(request):
       return Response('Hello')

   if __name__ == '__main__':
       app = StaticMiddleware(app, static_root='static', static_dirs=STATIC_DIRS)
       from wsgiref.simple_server import make_server
       httpd = make_server('', 8000, app)
       httpd.serve_forever()


WSGIのミドルウェアとして実装すると、フレームワークの実装に依存しません。
Bottleなどのフレームワークは静的ファイルの配信が少し貧弱ですが、ここで実装したミドルウェアで補うことが出来ます。

