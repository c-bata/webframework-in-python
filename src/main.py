from app import App, Response, JSONResponse
from wsgiref.simple_server import make_server
from wsgi_static_middleware import StaticMiddleware


app = App()


@app.route('^/$', 'GET')
def hello(request):
    return Response('Hello World')


@app.route('^/user/$', 'POST')
def create_user(request):
    return JSONResponse({'message': 'User Created'}, status=201)


@app.route('^/user/(?P<name>\w+)/$', 'GET')
def user_detail(request, name):
    return Response('Hello {name}'.format(name=name))


if __name__ == '__main__':
    app = StaticMiddleware(app, static_root='static')
    httpd = make_server('', 8000, app)
    httpd.serve_forever()
