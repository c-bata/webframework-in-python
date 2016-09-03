from app import App

app = App()


@app.route('^/$')
def index(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
    return [b'Top Page']


@app.route('^/users/$')
def index(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
    return [b'User List']

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    httpd.serve_forever()
