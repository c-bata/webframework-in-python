import os
from app import App, Response, TemplateResponse, JSONResponse
from wsgi_static_middleware import StaticMiddleware
from collections import OrderedDict

app = App()
BASE_DIR = os.path.dirname(__name__)
STATIC_DIR = os.path.join(BASE_DIR, 'static')


@app.route('/')
def index(request):
    users_link = app.router.reverse('user-list')
    return Response('Please go to {users}'.format(users=users_link))


@app.route('/users/', name='user-list')
def user_list(request):
    title = 'ユーザ一覧'
    users = [{'name': 'user{}'.format(i), 'id': i} for i in range(10)]
    response = TemplateResponse(filename='users.html', title=title, users=users)
    return response


@app.route('/users/{user_id}/', name='user-detail')
def user_detail(request, user_id: int):
    d = OrderedDict(
        user=user_id,
    )
    response = JSONResponse(dic=d, indent=4)
    return response


if os.environ.get('DEBUG'):
    app = StaticMiddleware(app, static_root='static', static_dirs=[STATIC_DIR])

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    httpd.serve_forever()
