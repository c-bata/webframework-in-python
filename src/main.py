from app import App, Response, TemplateResponse, JSONResponse
from wsgiref.simple_server import make_server


app = App()


@app.route('^/$', 'GET')
def hello(request):
    return Response('Hello World')


@app.route('^/user/$', 'POST')
def create_user(request):
    return JSONResponse({'message': 'User Created'}, status='201 Created')


@app.route('^/user/$', 'GET')
def users(request):
    users = ['user%s' % i for i in range(10)]
    return TemplateResponse('users.html', title='User List', users=users)


@app.route('^/user/(?P<name>\w+)$', 'GET')
def user_detail(request, name):
    return Response('Hello {name}'.format(name=name))


if __name__ == '__main__':
    httpd = make_server('', 8000, app)
    httpd.serve_forever()
