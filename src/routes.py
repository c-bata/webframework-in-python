import re
from collections import namedtuple


Route = namedtuple('Route', ['method', 'path', 'callback'])


class Router:
    def __init__(self):
        self.routes = []

    def add(self, method, path, callback):
        route = Route(method=method, path=path, callback=callback)
        self.routes.append(route)

    def match(self, method, path):
        for r in filter(lambda x: x.method == method.lower(), self.routes):
            matched = re.compile(r.path).match(path)
            if matched:
                kwargs = matched.groupdict()
                return r, kwargs
        return b'404 Not Found'
