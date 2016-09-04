# Framework
###########
import cgi
import re
from collections import namedtuple
from wsgiref.headers import Headers


Route = namedtuple('Route', ['method', 'path', 'callback'])


def http404(request):
    response = Response(body=[b'404 Not Found'], status='404 Not Found')
    return response


class Router:
    def __init__(self):
        self.routes = []

    def add(self, method, path, callback):
        route = Route(method=method, path=path, callback=callback)
        self.routes.append(route)

    def match(self, environ):
        method = environ['REQUEST_METHOD'].upper()
        path = environ['PATH_INFO'] or '/'

        for r in filter(lambda x: x.method == method.upper(), self.routes):
            matched = re.compile(r.path).match(path)
            if matched:
                kwargs = matched.groupdict()
                return r.callback, kwargs
        return http404, {}


class Request:
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
    def args(self):
        params = cgi.FieldStorage(
            environ=self.environ,
            keep_blank_values=True,
        )
        p = {k: params[k].value for k in params}
        return p

    @property
    def body(self):
        if self._body is None:
            content_length = int(self.environ.get('CONTENT_LENGTH', 0))
            self._body = self.environ['wsgi.input'].read(content_length).decode('utf-8')
        return self._body


class Response:
    default_status = '200 OK'
    default_content_type = 'text/html; charset=UTF-8'

    def __init__(self, body='', status=None, headers=None):
        self.body = body
        self.status = status or self.default_status
        self.headers = Headers()

        if headers:
            for name, value in headers.items():
                self.headers.add_header(name, value)

    @property
    def header_list(self):
        if 'Content-Type' not in self.headers:
            self.headers.add_header('Content-Type', self.default_content_type)
        out = [(key, value)
               for key in self.headers.keys()
               for value in self.headers.get_all(key)]
        return [(k, v.encode('utf8').decode('latin1')) for (k, v) in out]


class App:
    def __init__(self):
        self.router = Router()

    def route(self, path=None, method='GET', callback=None):
        def decorator(callback_func):
            self.router.add(method, path, callback_func)
            return callback_func
        return decorator(callback) if callback else decorator

    def __call__(self, env, start_response):
        callback, kwargs = self.router.match(env)
        request = Request(env)
        response = callback(request, **kwargs)
        start_response(response.status, response.header_list)
        return response.body

# Application
#############
app = App()


@app.route('^/users/$')
def user_list(request):
    response = Response(body=[b'User List'],
                        headers={'Content-type': 'text/plain; charset=utf-8'})
    return response


@app.route('^/users/(?P<user_id>\d+)/$')
def user_detail(request, user_id):
    res = 'Hello user {user_id}'.format(user_id=user_id)
    response = Response(body=[res.encode('utf-8')],
                        headers={'Content-type': 'text/plain; charset=utf-8'})
    return response

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    httpd.serve_forever()