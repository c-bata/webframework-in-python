from app import App, Response

app = App()


@app.route('^/users/$')
def user_list(request):
    response = Response(body='User List',
                        headers={'Content-type': 'text/plain; charset=utf-8'})
    return response


@app.route('^/users/(?P<user_id>\d+)/$')
def user_detail(request, user_id):
    response = Response(body='Hello user {user_id}'.format(user_id=user_id),
                        headers={'Content-type': 'text/plain; charset=utf-8'})
    return response

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    httpd.serve_forever()
