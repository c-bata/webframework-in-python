テンプレートエンジン
==========

BottleやDjangoのようなフレームワークでは自前でテンプレートエンジンを用意していますが、
今回は、デファクトスタンダードとなっているJinja2を使用しましょう。


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


