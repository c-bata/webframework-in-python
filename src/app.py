from wsgiref.simple_server import make_server


class App:
    def __call__(self, env, start_response):
        start_response('200 OK', [('Content-type', 'text/plain; charset=utf-8')])
        return [b'Hello World']

if __name__ == '__main__':
    app = App()
    httpd = make_server('', 8000, app)
    httpd.serve_forever()
