from wsgiref.simple_server import make_server


def application(env, start_response):
    start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
    return [b'Hello World']

if __name__ == '__main__':
    httpd = make_server('', 8000, application)
    httpd.serve_forever()
