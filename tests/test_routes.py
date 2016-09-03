from unittest import TestCase

from ..routes import Route, Router


def sample_callback():
    return b'body'


class RouteTests(TestCase):
    def test_route_length(self):
        route = Route('get', '/users/', sample_callback)
        self.assertEqual(len(route), 3)

    def test_route_has_method(self):
        route = Route('get', '/users/', sample_callback)
        self.assertEqual(route[0], 'get')
        self.assertEqual(route.method, 'get')


class RouterTests(TestCase):
    def test_add_router_add(self):
        router = Router()
        router.add('get', '^/users/$', sample_callback)
        self.assertEqual(len(router.routes), 1)
        self.assertIsInstance(router.routes[0], Route)
