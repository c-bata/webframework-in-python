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
- [ ] Creating request object: リクエストのenvironをうまくラップする
    - [ ] QueryParams (x-www-form-urlencoded) GETのクエリーパラメータの取得
    - [ ] BodyParams (x-www-form-urlencoded) POST等のクエリーパラメータの取得
    - [ ] request bodyの読み込み
    - [ ] jsonの読み込み
- [ ] Creating response object: レスポンスをうまくハンドリング
    - [ ] ヘッダーのコントロール
    - [ ] Cookieのコントロール
- [ ] Global object shared cross requests
- [ ] Basic static file serving for dev


時間があれば

- [ ] WSGI ミドルウェアの実装
    - [ ] フレームワークを作るまでしなくても十分活かせる内容だから是非話したい
- [ ] Template rendering


## jbkingさんのお言葉

- ちゃんとインタフェースを決めておく
    - Web ServerとApplicationはWSGI
    - Viewの責務はフレームワークでどこまでやるか？
        - DictならJSONにして、Headerもセットしたいかもしれない
        - view関数は、Responseオブジェクトを返すのか、unicodeとかbytesを返すのか
    - ここはある程度、口頭で説明することになるかな
- WSGIがyieldするとbyte列を返すようなオブジェクトになっている理由
    - 仮に、view関数が数100MBのレスポンスを生成する時に、全部メモリに載せるのは大変だから

## SLIDE.md

WSGIについての解説は [Python製Webフレームワークの設計と実装](https://speakerdeck.com/c_bata/how-to-develop-web-application-framework-in-python) をそのまま使いたい。
それ以外の部分の実装はMarkdown + Revealgoで書きながら進めていく。

方針としてはsphinxのbooksをまとめながら、画像ファイルとかを作成、static以下に配置していく。
そこの画像を参照していく。

sphinxのdocumentationもmarkdownで書くようにしたほうが、文言を使いまわし出来て都合がいいかもしれない。
sphinxのdocumentationはgithub-pages用のオプションを追加してるので、Readthedocsではなくそっちでみれるはず。
SLIDEはslideck.ioで公開。

```
$ revealgo SLIDE.md
```


## LICENSE

```
The MIT License (MIT)

Copyright (c) 2016 MASASHI Shibata

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
