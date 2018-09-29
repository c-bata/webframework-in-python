from .app import App, Response


app = App()


@app.route('^/$', 'GET')
def hello(request):
    return Response('Hello World')


@app.route('^/user/$', 'POST')
def create_user(request):
    return Response('User Created', status=201)


@app.route('^/user/(?P<name>\w+)$', 'GET')
def user_detail(request, name):
    return Response('Hello {name}'.format(name=name))
