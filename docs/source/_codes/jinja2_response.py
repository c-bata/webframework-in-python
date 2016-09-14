# Framework
############
import cgi
import os
import json
from jinja2 import Environment, FileSystemLoader
import re
from urllib.parse import parse_qs
from wsgiref.headers import Headers


def http404(request):
    return Response(body='404 Not Found', status='404 Not Found')


class Route:
    def __init__(self, method, path, callback):
        self.method = method.upper()
        self.path = path
        self.callback = callback

    def match(self, method, path):
        if self.method == method:
            return re.match(self.path, path)


class Router:
    def __init__(self):
        self.routes = []

    def add(self, method, path, callback):
        route = Route(method=method, path=path, callback=callback)
        self.routes.append(route)

    def match(self, environ):
        method = environ['REQUEST_METHOD'].upper()
        path = environ['PATH_INFO'] or '/'

        for r in self.routes:
            result = r.match(method, path)
            if result:
                kwargs = result.groupdict()
                return r.callback, kwargs
        return http404, {}


class Request:
    __slots__ = ('environ', '_body', )

    def __init__(self, environ):
        self.environ = environ
        self._body = None

    @property
    def forms(self):
        form = cgi.FieldStorage(
            fp=self.environ['wsgi.input'],
            environ=self.environ,
            keep_blank_values=True,
        )
        params = {k: form[k].value for k in form}
        return params

    @property
    def query(self):
        return parse_qs(self.environ['QUERY_STRING'])

    @property
    def body(self):
        if self._body is None:
            content_length = int(self.environ.get('CONTENT_LENGTH', 0))
            self._body = self.environ['wsgi.input'].read(content_length)
        return self._body

    @property
    def text(self, charset='utf-8'):
        return self.body.decode(charset)


class Response:
    __slots__ = ('_body', 'status', 'headers', 'charset')
    default_content_type = 'text/plain; charset=UTF-8'

    def __init__(self, body='', status='200 OK', headers=None, charset='utf-8'):
        self._body = body
        self.status = status
        self.headers = Headers()
        self.charset = charset

        if headers:
            for name, value in headers.items():
                self.headers.add_header(name, value)

    @property
    def body(self):
        if isinstance(self._body, str):
            return self._body.encode(self.charset)
        return self._body

    @property
    def header_list(self):
        if 'Content-Type' not in self.headers:
            self.headers.add_header('Content-Type', self.default_content_type)
        return self.headers.items()


class JSONResponse(Response):
    default_content_type = 'text/json; charset=UTF-8'

    def __init__(self, dic, status='200 OK', headers=None, charset='utf-8', **dump_args):
        super().__init__(json.dumps(dic, **dump_args),
                         status=status, headers=headers, charset=charset)


class TemplateResponse(Response):
    default_content_type = 'text/html; charset=UTF-8'

    def __init__(self, filename, status='200 OK', headers=None, charset='utf-8', **tpl_args):
        template = config.jinja2_env.get_template(filename)
        super().__init__(template.render(**tpl_args),
                         status=status, headers=headers, charset=charset)


class Config(dict):
    default_config = {
        'TEMPLATE_DIR': os.path.join(os.path.abspath('.'), 'templates'),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update(self.default_config)

    @property
    def jinja2_env(self):
        return Environment(loader=FileSystemLoader(self['TEMPLATE_DIR']))

config = None


class App:
    def __init__(self):
        global config
        config = Config()
        self.router = Router()

    def route(self, path=None, method='GET', callback=None):
        def decorator(callback_func):
            self.router.add(method, path, callback_func)
            return callback_func
        return decorator(callback) if callback else decorator

    def wsgi(self, env, start_response):
        callback, kwargs = self.router.match(env)
        request = Request(env)
        response = callback(request, **kwargs)
        start_response(response.status, response.header_list)
        return [response.body]

    def __call__(self, env, start_response):
        return self.wsgi(env, start_response)


# Application
##############
from collections import OrderedDict

app = App()


@app.route('^/$')
def index(request):
    return Response('Hello World')


@app.route('^/users/$')
def user_list(request):
    title = 'ユーザ一覧'
    users = ['user{}'.format(i) for i in range(10)]
    response = TemplateResponse(filename='users.html', title=title, users=users)
    return response


@app.route('^/users/(?P<user_id>\d+)/$')
def user_detail(request, user_id):
    d = OrderedDict(
        user=user_id,
    )
    response = JSONResponse(dic=d, indent=4)
    return response

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    httpd.serve_forever()
