import re
from collections import namedtuple


Route = namedtuple('Route', ['method', 'path', 'callback'])


def http404(env, start_response):
    start_response('404 Not Found', [('Content-type', 'text/plain; charset=utf-8')])
    return [b'404 Not Found']


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
        return callback(env, start_response, **kwargs)
