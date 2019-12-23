こんにちは、芝田 将 ( `@c_bata_ <https://twitter.com/c_bata_>`_ ) です。

この資料はPyCon JP 2016で行った `「基礎から学ぶWebアプリケーションフレームワークの作り方」 <https://pycon.jp/2016/ja/schedule/presentation/14/>`_ の書き起こし資料です。
誤字等があれば、Issue or PRをお待ちしております。

.. raw:: html

   <a href="http://b.hatena.ne.jp/entry/s/c-bata.link/webframework-in-python/" class="hatena-bookmark-button" data-hatena-bookmark-layout="vertical-normal" data-hatena-bookmark-lang="ja" title="このエントリーをはてなブックマークに追加"><img src="https://b.st-hatena.com/images/entry-button/button-only@2x.png" alt="このエントリーをはてなブックマークに追加" width="20" height="20" style="border: none;" /></a><script type="text/javascript" src="https://b.st-hatena.com/js/bookmark_button.js" charset="utf-8" async="async"></script>
   <a data-pocket-label="pocket" data-pocket-count="vertical" class="pocket-btn" data-lang="en"></a>

はじめに
========

この資料では200行に満たないシンプルなWebフレームワークの作り方をボトムアップで解説します。
テンプレートエンジンとしてJinja2を使ったりもしますが、基本的にはPythonの標準ライブラリのみを使っています。
FlaskやDjango等を使ったWeb開発の経験があり、基本的なHTTPの知識があれば読み進められるんじゃないかなと思うのでぜひチャレンジしてみてください。

本資料を読み終えた方はBottleやDjango、筆者の公開している `Kobin <https://github.com/kobinpy/kobin>`_ というフレームワークのコードを
読んでみたり、自分でWSGIフレームワークを実装してみるのもいいかもしれません。
また最近ではASGIのフレームワークも増えてきましたが、そちらの解説もまたタイミングがあればどこかに書こうかと思います。


目次
====

.. toctree::
   :maxdepth: 2

   wsgi
   routing
   request
   response
   template
   middleware


関連URL
=======

* `Github <https://github.com/c-bata/webframework-in-python>`_ ( `WSGIフレームワーク <https://github.com/c-bata/webframework-in-python/blob/master/src/app.py>`_  / `WSGIサーバー <https://github.com/c-bata/webframework-in-python/blob/master/src/wsgi_server.py>`_ / `サンプルアプリケーション <https://github.com/c-bata/webframework-in-python/blob/master/src/main.py>`_ )
* `スライド <https://c-bata.link/webframework-in-python/slide.html#1>`_
* `動画(Youtube) <https://www.youtube.com/watch?v=S-InxJA5NOg>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
