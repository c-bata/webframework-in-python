# Webアプリケーションフレームワークの作り方

このリポジトリはPyCon JP 2016「基礎から学ぶWebアプリケーション・フレームワーク」の発表資料です。

- 解説ページ : http://c-bata.link/webframework-in-python/index.html
- スライド : http://c-bata.link/webframework-in-python/slide.html


## 発表の上で大事なポイント

- ストーリーと共感
    - わかる〜 でもやったことない
    - ユーザにも、自分ならこう考えるなっていう思考をさせる。眠たくならない

- 聞きにきてくれた人が次の日から何をしてほしい？
    - どうなってほしかったかは間違えちゃダメ。
    - KobinとかBottle読んで欲しい
    - FWを読むきっかけを作って欲しい
        - どう作られてるかを知れる。
        - それならどういう構成要素があるのか。
        - 自分が何か困ったときに、どこに問題があるのかを読みやすくなった(体験談)。

- FWのコードを書いてるのか、アプリケーションのコードを書いてるのかをしっかり伝える

- 満たすべきWSGIの世界
    - callableであればいい
    - クラスでもcallableであれば、WSGIアプリケーション
- FWの話
- ユーザが書いてるコードの世界
    - 
    - view関数を用意して

- view関数にenvとstart_responseがきたら面倒だよね。
    - requestオブジェクトというものを渡しましょう
    - responseオブジェクトというものを渡しましょう

WSGIの話
クラスを用意してる

ゴールを決めて、流れを決める


## jbkingさんのお言葉

- ちゃんとインタフェースを決めておく
    - Web ServerとApplicationはWSGI
    - Viewの責務はフレームワークでどこまでやるか？
        - DictならJSONにして、Headerもセットしたいかもしれない
        - view関数は、Responseオブジェクトを返すのか、unicodeとかbytesを返すのか
    - ここはある程度、口頭で説明することになるかな

徐々に必要な機能を追加していこう。
その度に図を書きなおしていこう。


## LICENSE

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />WebFramework in Python by Masashi Shibata is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.
