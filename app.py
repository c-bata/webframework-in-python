import cgi
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
    __slots__ = ('_body', 'status', 'headers')
    default_status = '200 OK'
    default_content_type = 'text/html; charset=UTF-8'

    def __init__(self, body='', status=None, headers=None):
        self._body = body
        self.status = status or self.default_status
        self.headers = Headers()

        if headers:
            for name, value in headers.items():
                self.headers.add_header(name, value)

    @property
    def body(self):
        if isinstance(self._body, str):
            return self._body.encode('utf-8')
        return self._body

    @property
    def header_list(self):
        if 'Content-Type' not in self.headers:
            self.headers.add_header('Content-Type', self.default_content_type)
        return self.headers.items()


class App:
    def __init__(self):
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
