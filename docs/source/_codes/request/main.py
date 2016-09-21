from app import App
from wsgiref.simple_server import make_server


app = App()


@app.route('^/$', 'GET')
def hello(request, start_response):
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
    return [b'Hello World']


@app.route('^/user/(?P<name>\w+)$', 'GET')
def user_detail(request, start_response, name):
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
    body = 'Hello {name}'.format(name=name)
    return [body.encode('utf-8')]


if __name__ == '__main__':
    httpd = make_server('', 8000, app)
    httpd.serve_forever()
