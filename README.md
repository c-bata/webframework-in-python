# Webアプリケーションフレームワークの作り方

このリポジトリはPyCon JP 2016「基礎から学ぶWebアプリケーション・フレームワーク」の発表用補足資料です。

ストーリーと共感
わかる〜 でもやったことない
ユーザにも、自分ならこう考えるなっていう思考をさせる

聞きにきてくれた人が次の日から何をしてほしい？ KobinとかBottle読んで欲しい

どうなってほしかったかは間違えちゃダメ。

FWを読むきっかけを作って欲しい
どう作られてるかを知れる。
それならどういう構成要素があるのか。
自分が何か困ったときに、どこに問題があるのかを読みやすくなった(体験談)。

まずどこを知らないといけないか？
自分たちのアプリケーションってなんかgunicornとかで動かしてる。
サーバとアプリケーションがやり取りしてるはず。そこのインタフェースについて勉強してみよう。

FWのコードを書いてるのか、アプリケーションのコードを書いてるのかをしっかり伝える


WSGIの話
Webアプリケーション・フレームワークというタイトルですが、今回はWSGIのアプリケーションのためのフレームワークに焦点をあてて勉強していきましょう


FWの構成要素を図で

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




## 手順

Webアプリケーション・フレームワークの実装手順。

- [x] Hello World with wsgiref
- [x] Creating Kobin class
    - [x] Define `__call__` method
- [x] ルーティングの実装
    - [x] 正規表現ベースのルーティングの方法を解説
        - パフォーマンス面・逆引き難しい問題についても触れる
    - [x] 1つのRouteの情報をラップするRouteクラス(namedtuple)
    - [x] リクエストのURLとメソッドに応じて、適切な関数を呼び出すRouterクラス
- [x] Creating request object: リクエストのenvironをうまくラップする
    - [x] QueryParams (x-www-form-urlencoded) GETのクエリーパラメータの取得
    - [x] BodyParams (x-www-form-urlencoded) POST等のクエリーパラメータの取得
    - [x] request bodyの読み込み
    - [ ] jsonの読み込み
- [x] Creating response object: レスポンスをうまくハンドリング
    - [x] ヘッダーのコントロール
    - [x] Cookieのコントロール
- [x] Middleware
    - [x] Basic static file serving for dev
- [x] Template rendering using Jinja2


## jbkingさんのお言葉

- ちゃんとインタフェースを決めておく
    - Web ServerとApplicationはWSGI
    - Viewの責務はフレームワークでどこまでやるか？
        - DictならJSONにして、Headerもセットしたいかもしれない
        - view関数は、Responseオブジェクトを返すのか、unicodeとかbytesを返すのか
    - ここはある程度、口頭で説明することになるかな
- WSGIがyieldするとbyte列を返すようなオブジェクトになっている理由
    - 仮に、view関数が数100MBのレスポンスを生成する時に、全部メモリに載せるのは大変だから

徐々に必要な機能を追加していこう。
その度に図を書きなおしていこう。


## LICENSE

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />WebFramework in Python by Masashi Shibata is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.
