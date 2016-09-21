# Framework
############
import cgi
import json
from jinja2 import Environment, PackageLoader
from typing import get_type_hints
from urllib.parse import parse_qs
from wsgiref.headers import Headers

DEFAULT_ARG_TYPE = str


def http404(request):
    return Response(body='404 Not Found', status='404 Not Found')


def split_by_slash(path):
    stripped_path = path.lstrip('/').rstrip('/')
    return stripped_path.split('/')


class Route:
    def __init__(self, rule, method, name, callback):
        self.rule = rule
        self.method = method.upper()
        self.name = name
        self.callback = callback

    @property
    def callback_types(self):
        return get_type_hints(self.callback)

    def get_typed_url_vars(self, url_vars):
        typed_url_vars = {}
        for k, v in url_vars.items():
            arg_type = self.callback_types.get(k, DEFAULT_ARG_TYPE)
            typed_url_vars[k] = arg_type(v)
        return typed_url_vars

    def _match_method(self, method):
        return self.method == method.upper()

    def _match_path(self, path):
        split_rule = split_by_slash(self.rule)
        split_path = split_by_slash(path)
        url_vars = {}

        if len(split_rule) != len(split_path):
            return None

        for r, p in zip(split_rule, split_path):
            if r.startswith('{') and r.endswith('}'):
                url_var_key = r.lstrip('{').rstrip('}')
                url_vars[url_var_key] = p
                continue
            if r != p:
                return None
        return self.get_typed_url_vars(url_vars)

    def match(self, method, path):
        if not self._match_method(method):
            return None

        url_vars = self._match_path(path)
        if url_vars is not None:
            return self.get_typed_url_vars(url_vars)


class Router:
    def __init__(self):
        self.routes = []

    def match(self, environ):
        method = environ['REQUEST_METHOD'].upper()
        path = environ['PATH_INFO'] or '/'

        for route in self.routes:
            url_vars = route.match(method, path)
            if url_vars is not None:
                return route.callback, url_vars
        return http404, {}

    def add(self, method, rule, name, callback):
        route = Route(method=method.upper(), rule=rule, name=name, callback=callback)
        self.routes.append(route)

    def reverse(self, name, **kwargs):
        for route in self.routes:
            if name == route.name:
                return route.rule.format(**kwargs)


class Request:
    __slots__ = ('environ', '_body', 'charset',)

    def __init__(self, environ, charset='utf-8'):
        self.environ = environ
        self.charset = charset
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
    def body(self) -> bytes:
        if self._body is None:
            content_length = int(self.environ.get('CONTENT_LENGTH', 0))
            self._body = self.environ['wsgi.input'].read(content_length)
        return self._body

    @property
    def text(self):
        return self.body.decode(self.charset)


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
        'TEMPLATE_DIR': 'templates',
    }

    def __init__(self, module_name, **kwargs):
        super().__init__(**kwargs)
        self.module_name = module_name
        self.update(self.default_config)
        self.jinja2_env = Environment(loader=PackageLoader(self.module_name, self['TEMPLATE_DIR']))

config = None


class App:
    def __init__(self, module_name):
        self.router = Router()

        global config
        config = Config(module_name)
        config.jinja2_env.globals.update(
            reverse=self.router.reverse
        )

    def route(self, rule=None, method='GET', name='', callback=None):
        def decorator(callback_func):
            self.router.add(method, rule, name, callback_func)
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
import os
from collections import OrderedDict

app = App(__name__)
BASE_DIR = os.path.dirname(__name__)
STATIC_DIR = os.path.join(BASE_DIR, 'static')


@app.route('/')
def index(request):
    users_link = app.router.reverse('user-list')
    return Response('Please go to {users}'.format(users=users_link))


@app.route('/users/', name='user-list')
def user_list(request):
    title = 'ユーザ一覧'
    users = [{'name': 'user{}'.format(i), 'id': i} for i in range(10)]
    response = TemplateResponse(filename='users.html', title=title, users=users)
    return response


@app.route('/users/{user_id}/', name='user-detail')
def user_detail(request, user_id: int):
    d = OrderedDict(
        user=user_id,
    )
    response = JSONResponse(dic=d, indent=4)
    return response

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    httpd.serve_forever()
