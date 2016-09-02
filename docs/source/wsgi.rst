WSGI とは？
===========

Webサーバとのやりとり
---------------------

PythonではWebサーバとしてgunicornやuWSGIが広く利用されています。
Webアプリを開発する際には、このサーバ上で作成したアプリケーションを動かしますが、
具体的にWebサーバと私達の開発しているアプリケーションがどのようなやりとりを行っているのか、日頃の開発で意識するシーンは少ないでしょう。
しかし、Webフレームワークを開発するとなるとどのようにやり取りが行われているのかを知る必要があります。

PythonではWebサーバとのやり取りの方法としてPEP3333で定義されたWSGI(Web Server Gateway Interface) v1.0.1という仕様が広く利用されています。
それではWSGIについて勉強していきましょう。


WSGI(Web Server Gateway Interface)
----------------------------------

WSGIの仕様を全て読むのは大変なので、実際のPythonのコードをベースに理解していきましょう。

.. code-block:: python

   def application(env, start_response)
       start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
       return [b'Hello World']

この3行のPythonのコードはWSGIの仕様を満たしています。

1. 2つの引数を持った呼び出し可能なオブジェクト
2. 第2引数として渡されたオブジェクトを呼び出し、HTTPステータスコードとヘッダ情報を渡す
3. レスポンスボディとしてバイト文字列をyieldするiterableなオブジェクトを返す

それでは実際に動かしてみましょう。
さきほど上げた3行のPythonのコードが本当にWSGIの仕様を満たしているのであれば、
gunicornやuWSGIなどのWSGIサーバで動かすことが出来るはずです。
上のコードを `hello.py` という名前で保存し、下記のコマンドを実行してください。

.. code-block::

   $ pip install gunicorn
   $ gunicorn -w 1 hello:application

動きましたか？正常に動作した場合はWebブラウザなどでアクセスすると `Hello World` と表示されるはずです。
それでは次の章でこれから作るWebフレームワークに必要な機能を考えていきましょう。


.. note::

   Pythonの標準モジュールの中にも、WSGIのリファレンス実装があります。
   シングルスレッドでしか動作しないなど、機能的には gunicorn 等に劣りますが、
   標準モジュールに含まれているため、開発やデバッグ等に活用すると便利です。

   .. literalinclude:: _codes/helloworld.py

