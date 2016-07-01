# Webアプリケーションフレームワークの作り方

このリポジトリはPyCon JP 2016「基礎から学ぶWebアプリケーション・フレームワーク」の発表用補足資料です。


## 手順

Webアプリケーション・フレームワークの実装手順。

- [ ] Hello World with wsgiref
- [ ] Creating Kobin class
    - [ ] Define `__call__` method
- [ ] ルーティングの実装
    - [ ] 正規表現ベースのルーティングの方法を解説
        - パフォーマンス面・逆引き難しい問題についても触れる
    - [ ] 1つのRouteの情報をラップするRouteクラス
    - [ ] リクエストのURLとメソッドに応じて、適切な関数を呼び出すRouterクラス
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
