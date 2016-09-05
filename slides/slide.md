# 基礎から学ぶWebアプリケーションフレームワークの作り方

Masashi Shibata (`@c_bata_`)

PyConJP 2016

2016/09/21 (Wed)


---
# 自己紹介

![プロフィールアイコン](./img/profile.png)

- 芝田 将
- 明石高専 専攻科
- PyCon JP 2015, 2016 スタッフ
- PyCon Taiwan 2015, JP 2015, Korea 2016 でLTしてきました

念願のトークセッション :)


???

ジョブズはiPhoneの発表日に、 This is the day (この日を待ってたんだ)って言ったらしい。
意気込みを伝えたい。堂々としたい。価値を届けるんだっていいたい


---
# 動機と目的

何か躓いた時に、自分で修正したい。そもそもバグなのか調べたい。

???
- 何かOSSのライブラリとかのコードを読んで勉強してみたいなと思った
- 自分はWebのサーバサイドエンジニアを目指してる学生なので、一番良く使っているのは FlaskやDjango だろう
- これからサーバサイドをメインに頑張っていくのなら、ただフレームワークを使えるのではなくて実装まで意識できる。何か困ったことがあれば自分で直せるエンジニアになりたかった
- でもシンプルで読みやすいと言われていたBottleのコードも全く読めない。何から手を付ければいいのか分からなかった。

---
# みなさんに持ち帰って欲しい内容

- Webフレームワークの構成要素とそれぞれの目的をしっかり覚えて帰ってください。
    - あとはコードを読んで理解できるはずです。
- 細かい部分は、Youtube, Sphinxで復習してください。
- それが終わったらBottleかKobinの実装を読んでみてください
    - Kobinはversionを3.5に絞っていて、Type Hintsもあり読みやすいと思います :)

???
最終的に出来上がるアプリケーションは150行ほどです。
かなり短い方ですが、話を聞きながら細かい実装まで全てをこのセッション中に全員が理解するのは難しいかと思います。


---
# コードを読んでみよう

自分が分かってないところを整理。


???

- Bottleのコードを読み始めた。
- 全く分からない


---
# サーバとの通信

- gunicornとかuWSGIで動かす
- そういうサーバとはどうやって通信するんだろう？
    - 何か共通のインタフェースがあるはず

???


---
# WSGIについて

TODO: ここはKeynoteで作ってたやつ使い回す


---
# gunicornで動かしてみる

```bash
$ gunicorn -w 1 hello:app
```


???
本当にさっきの3行のアプリケーションが動いた :)
これを拡張していけばよさそうだ。
何をどう拡張しよう。


---
# 拡張をするまえに

関数のままでは機能追加が難しそうだ :(

```python
from flask import Flask

app = Flask(__name__)
:
```

???
そういえば形式が違う。
オブジェクトを


---
# `__call__` メソッド

関数のままでは機能追加が難しそうだ :(

```python
class App:
    def __call__(self, env, start_response):
        start_response('200 OK', [('Content-type', 'text/plain')])
        return [b'Hello World']
```

???
これの紹介は、RouteクラスとRouterクラスを実装したあとに、Appに組み込む時にしたほうが流れとして自然。

---
# ルーティング

```python
app = App()

@app.route('^/users/$')
def users(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    return 
```

???

今のアプリケーションはどこにいっても


---
# リクエストオブジェクト

全部に、envとstart_responseを渡すのは面倒そうだ


---
# リクエストボディの取得

```python
@property
def body(self):
    if self._body is None:
        content_length = int(self.environ.get('CONTENT_LENGTH', 0))
        self._body = self.environ['wsgi.input'].read(content_length)
    return self._body

@property
def text(self, charset='utf-8'):
    return self.body.decode(charset)
```


---
# GETのクエリパラメータの取得

application/x-www-form-urlencoded 型のデータに対しては、 `urllib.parse.parse_qs` を利用する

```python
>>> from urllib.parse import parse_qs
>>> parse_qs('foo=bar&hoge=fuga')
{'hoge': ['fuga'], 'foo': ['bar']}
```


---
# POSTのクエリパラメータの取得

cgi.FieldStorage を利用する

```python
@property
def forms(self):
    form = cgi.FieldStorage(
        fp=self.environ['wsgi.input'],
        environ=self.environ,
        keep_blank_values=True,
    )
    params = {k: form[k].value for k in form}
    return params
```


---
# レスポンスオブジェクト

- ヘッダ
- ステータス
- ボディ


---
# ヘッダ

```python
>>> from wsgiref.headers import Headers
>>> h = Headers()
>>> h.add_header('Content-type', 'text/plain')
>>> h.add_header('Foo', 'bar')
>>> h.items()
[('Content-type', 'text/plain'), ('Foo', 'bar')]
```


---
# Webフレームワークの作り方

Pythonの具体的なコードをベースにWebアプリケーションフレームワークを作る上で必要となる知識について解説します。
Hello Worldをスタートとして、ルーティングやリクエスト・レスポンスのハンドリング方法、CSSやJS等の静的ファイルの扱いなどWebアプリケーションフレームワークに必要な機能とその実装方法を解説します。


---
# Kobinの紹介

私が開発しているKobinというフレームワークと、それを用いた実際のアプリケーションを紹介します。
Kobinは本発表で紹介した機能を全て実装していますが、その実装は800行に満たない程度(5/17現在)と非常に短く、勉強用途としては最適なWebフレームワークとなっています。
またType Hintsを活用しているためコードを読む上での手がかりとなる情報も既存のフレームワークに比べ多いでしょう。


---
# まとめ


