================================
Webアプリケーションフレームワークの作り方 in Python
================================

こんにちは、芝田 将 ( `@c_bata_ <https://twitter.com/c_bata_>`_ ) です。

この資料はPyCon JP 2016で行った `「基礎から学ぶWebアプリケーションフレームワークの作り方」 <https://pycon.jp/2016/ja/schedule/presentation/14/>`_ の書き起こし資料です。
誤字等があれば、Issue or PRをお待ちしております。

.. raw:: html

   <a href="http://b.hatena.ne.jp/entry/s/c-bata.link/webframework-in-python/" class="hatena-bookmark-button" data-hatena-bookmark-layout="vertical-normal" data-hatena-bookmark-lang="ja" title="このエントリーをはてなブックマークに追加"><img src="https://b.st-hatena.com/images/entry-button/button-only@2x.png" alt="このエントリーをはてなブックマークに追加" width="20" height="20" style="border: none;" /></a><script type="text/javascript" src="https://b.st-hatena.com/js/bookmark_button.js" charset="utf-8" async="async"></script>
   <a data-pocket-label="pocket" data-pocket-count="vertical" class="pocket-btn" data-lang="en"></a>

はじめに
========

筆者は自分の一番の強みをサーバサイドにしようと決めた時、まずはDjangoやFlaskなど主要なWebフレームワークの実装を知っておきたいと思いました。
何らかのバグにぶつかった時に、自分でも修正できるようにしておきたいからです。
そこで学生時代に、BottleやFlaskの実装を読み進めていました。
最初はどこから手をつけて読んでいけばいいかも分かりませんでしたが、頭を抱えながらも読み進めることで各種WSGIフレームワークの全体像が見えるようになってきました。
各種フレームワークの設計方針の違いに気づき、フレームワークを利用しているだけでは気づくことのできなかった多くのHTTPに関する知識を得ることができました。
最近ではGo言語などPython以外の言語を書くことも多くなってきましたが、ここで得た多くの知識が役に立ったと感じています。

とはいえ筆者のように知識が浅いまま、最初から数千行〜数十万行のコードベースを読み進めるのは非常に大変です。
この資料では200行に満たないシンプルなWebフレームワークの作り方をボトムアップで解説します。
小さなフレームワークを1から作ってみることは、全体像を把握するのに有効なやり方です。
ここで解説する内容を抑えておけば、Bottleの実装を読むことにはそれほど苦労しないでしょう。
またFlaskやDjangoを読むときにも全体像を把握しながら読み進められれば、どこから手をつければいいかも想像がつきます。


対象読者
--------

この資料では、実際にPythonでWebアプリケーションのフレームワークを作っていきます。
そのため既にWeb開発の経験があり、基本的なHTTPの知識があると理解がしやすいかと思います。
もし読み進めていく中で難しいと感じた場合は、これらの知識をもう少し復習してみるといいかもしれません。
どうしてもわからない場合はGithubの方にIssueをたてていただけると、そのあたりの補足説明を増やせるかもしれません。
お気軽に連絡ください。


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
