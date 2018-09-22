import os
import re
import cgi
import itertools
import json
from urllib.parse import parse_qs
from wsgiref.headers import Headers
from jinja2 import Environment, FileSystemLoader


def http404(request):
    return Response('404 Not Found', status='404 Not Found')


def http405(request):
    return Response('405 Method Not Allowed', status='405 Method Not Allowed')


class Router:
    def __init__(self):
        self.routes = []

    def add(self, method, path, callback):
        self.routes.append({
            'method': method,
            'path': path,
            'callback': callback
        })

    def match(self, method, path):
        routes_grouped_by_path = itertools.groupby(
            sorted(self.routes, key=lambda x: x['path']), key=lambda x: x['path']
        )

        for p, routes in routes_grouped_by_path:
            matched = re.compile(p).match(path)
            if not matched:
                continue

            url_vars = matched.groupdict()
            for r in routes:
                if method.upper() == r['method']:
                    return r['callback'], url_vars
            return http405, {}
        return http404, {}


class Request:
    def __init__(self, environ, charset='utf-8'):
        self.environ = environ
        self._body = None
        self.charset = charset

    @property
    def path(self):
        return self.environ['PATH_INFO'] or '/'

    @property
    def method(self):
        return self.environ['REQUEST_METHOD'].upper()

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
    def text(self):
        return self.body.decode(self.charset)

    @property
    def json(self):
        return json.loads(self.body)


class Response:
    default_status = '200 OK'
    default_content_type = 'text/html; charset=UTF-8'

    def __init__(self, body='', status=None, headers=None, charset='utf-8'):
        self._body = body
        self.status = status or self.default_status
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


class TemplateResponse(Response):
    default_content_type = 'text/html; charset=UTF-8'

    def __init__(self, filename, status='200 OK', headers=None, charset='utf-8', **tpl_args):
        self.filename = filename
        self.tpl_args = tpl_args
        super().__init__(body='', status=status, headers=headers, charset=charset)

    def render_body(self, jinja2_environment):
        template = jinja2_environment.get_template(self.filename)
        return template.render(**self.tpl_args).encode(self.charset)


class JSONResponse(Response):
    default_content_type = 'text/json; charset=UTF-8'

    def __init__(self, dic, status='200 OK', headers=None, charset='utf-8', **dump_args):
        self.dic = dic
        self.json_dump_args = dump_args
        super().__init__('', status=status, headers=headers, charset=charset)

    @property
    def body(self):
        return json.dumps(self.dic, **self.json_dump_args).encode(self.charset)


class App:
    def __init__(self, templates=None):
        self.router = Router()
        if templates is None:
            templates = [os.path.join(os.path.abspath('.'), 'templates')]
        self.jinja2_environment = Environment(loader=FileSystemLoader(templates))

    def route(self, path=None, method='GET', callback=None):
        def decorator(callback_func):
            self.router.add(method, path, callback_func)
            return callback_func
        return decorator(callback) if callback else decorator

    def __call__(self, env, start_response):
        request = Request(env)
        callback, kwargs = self.router.match(request.method, request.path)

        response = callback(request, **kwargs)
        start_response(response.status, response.header_list)
        if isinstance(response, TemplateResponse):
            return [response.render_body(self.jinja2_environment)]
        return [response.body]
