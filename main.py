from app import App

app = App()


@app.route('^/users/$')
def user_list(request, start_response):
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
    print(request.args)
    return [b'User List']


@app.route('^/users/(?P<user_id>\d+)/$')
def user_detail(request, start_response, user_id):
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
    res = 'Hello user {user_id}'.format(user_id=user_id)
    return [res.encode('utf-8')]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    httpd.serve_forever()
