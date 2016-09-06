import cgi
import json
from jinja2 import Environment, PackageLoader
from typing import get_type_hints
from urllib.parse import parse_qs
from wsgiref.headers import Headers

from typing import Callable, Dict, List, Tuple, Union, Any  # type: ignore

DEFAULT_ARG_TYPE = str


def http404(request):
    return Response(body='404 Not Found', status='404 Not Found')


def split_by_slash(path: str) -> List[str]:
    stripped_path = path.lstrip('/').rstrip('/')
    return stripped_path.split('/')


class Route:
    """ This class wraps a route callback along with route specific metadata.
        It is also responsible for turing an URL path rule into a regular
        expression usable by the Router.
    """
    def __init__(self, rule: str, method: str, name: str,
                 callback: Callable[..., Union[str, bytes]]) -> None:
        self.rule = rule
        self.method = method.upper()
        self.name = name
        self.callback = callback

    @property
    def callback_types(self) -> Dict[str, Any]:
        return get_type_hints(self.callback)

    def get_typed_url_vars(self, url_vars: Dict[str, str]) -> Dict[str, Any]:
        typed_url_vars = {}  # type: Dict[str, Any]
        for k, v in url_vars.items():
            arg_type = self.callback_types.get(k, DEFAULT_ARG_TYPE)
            typed_url_vars[k] = arg_type(v)
        return typed_url_vars

    def _match_method(self, method: str) -> bool:
        return self.method == method.upper()

    def _match_path(self, path: str) -> Dict[str, Any]:
        split_rule = split_by_slash(self.rule)
        split_path = split_by_slash(path)
        url_vars = {}  # type: Dict[str, str]

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

    def match(self, method: str, path: str) -> Dict[str, Any]:
        if not self._match_method(method):
            return None

        url_vars = self._match_path(path)
        if url_vars is not None:
            return self.get_typed_url_vars(url_vars)


class Router:
    def __init__(self) -> None:
        self.routes = []  # type: List[Route]

    def match(self, environ: Dict[str, str]) -> Tuple[Callable[..., 'Response'], Dict[str, Any]]:
        method = environ['REQUEST_METHOD'].upper()
        path = environ['PATH_INFO'] or '/'

        for route in self.routes:
            url_vars = route.match(method, path)
            if url_vars is not None:
                return route.callback, url_vars
        return http404, {}

    def add(self, method: str, rule: str, name: str,
            callback: Callable[..., Union[str, bytes]]) -> None:
        """ Add a new rule or replace the target for an existing rule. """
        route = Route(method=method.upper(), rule=rule, name=name, callback=callback)
        self.routes.append(route)

    def reverse(self, name, **kwargs) -> str:
        for route in self.routes:
            if name == route.name:
                return route.rule.format(**kwargs)


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
