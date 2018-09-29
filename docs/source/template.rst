JSONやHTMLを返す
===============

*この章はまだ書き途中です。気が向いたときに書き直していきますがこの資料の感想をいただけると頑張るかもしれません*

JSONResponseクラスを用意する
----------------------------------

Responseオブジェクトは文字列を返すのには非常に向いていました。
実際Webアプリケーションを開発する中ではこのように文字列を返すことはあまりなく、
Webブラウザで表示するためのHTMLを返したり、クライアントアプリケーションのためにJSON形式のAPIを用意することのほうが多くあります。
まずはJSON APIの開発に便利な JSONResponse クラスを用意してみましょう。

.. code-block:: python

   class JSONResponse(Response):
       default_content_type = 'text/json; charset=UTF-8'

       def __init__(self, dic, status=200, headers=None, charset=None, **dump_args):
           self.dic = dic
           self.json_dump_args = dump_args
           super().__init__('', status=status, headers=headers, charset=charset)

       @property
       def body(self):
           return [json.dumps(self.dic, **self.json_dump_args).encode(self.charset)]



Jinja2を使ってHTMLを返す
-----------------------------

BottleやDjangoのようなフレームワークでは自前でテンプレートエンジンを用意していますが、
今回は、デファクトスタンダードとなっているJinja2を使ってHTMLを返していきましょう。

Jinja2 おさらい
~~~~~~~~~~~

Jinja2の使い方をおさらいしてみましょう.

.. code-block:: python

   >>> import os
   >>> from jinja2 import Environment, FileSystemLoader
   >>>
   >>> templates = [os.path.join(os.path.abspath('.'), 'templates')]
   >>> env = Environment(loader=FileSystemLoader(templates))
   >>> template = env.get_tempplate('users.html')
   >>> template.render(title='Hello World', users=['user1', 'users2'])


TemplateResponse クラス
~~~~~~~~~~~~~~~~~~~

それではこれを簡単に扱えるようなResponseクラスを用意します。


.. code-block:: python

   class TemplateResponse(Response):
       default_content_type = 'text/html; charset=UTF-8'

       def __init__(self, filename, status='200 OK', headers=None, charset='utf-8', **tpl_args):
           self.filename = filename
           self.tpl_args = tpl_args
           super().__init__(body='', status=status, headers=headers, charset=charset)

       def render_body(self, jinja2_environment):
           template = jinja2_environment.get_template(self.filename)
           return template.render(**self.tpl_args).encode(self.charset)

render_bodyを呼び出す際に、environmentを渡す必要があるため、つぎのようにAppクラスを書き換えましょう.


.. code-block:: python

   from jinja2 import Environment, FileSystemLoader

   class App:
       def __init__(self, templates=None):
           self.router = Router()
           if templates is None:
               templates = [os.path.join(os.path.abspath('.'), 'templates')]
           self.jinja2_environment = Environment(loader=FileSystemLoader(templates))

       (中略)

       def __call__(self, env, start_response):
           method = env['REQUEST_METHOD'].upper()
           path = env['PATH_INFO'] or '/'
           callback, kwargs = self.router.match(method, path)

           response = callback(Request(env), **kwargs)
           start_response(response.status, response.header_list)
           if isinstance(response, TemplateResponse):
               return [response.render_body(self.jinja2_environment)]
           return [response.body]


これで実装はOKです。使ってみましょう。

`main.py`

.. code-block:: python

   @app.route('^/user/$', 'GET')
   def users(request):
       users = ['user%s' % i for i in range(10)]
       return TemplateResponse('users.html', title='User List', users=users)


`templates/users.html`

.. code-block:: html

   <!DOCTYPE html>
   <html lang="ja">
   <head>
       <meta charset="UTF-8">
       <title>{{ title }}</title>
   </head>
   <body>
       <ul>
           {% for user in users %}
           <li>{{ user }}</li>
           {% endfor %}
       </ul>
   </body>
   </html>


