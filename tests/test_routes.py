import unittest

from src.app import Router


def sample_callback():
    return b'body'


class RouterTests(unittest.TestCase):
    def test_add_router_add(self):
        router = Router()
        router.add('get', '^/users/$', sample_callback)
        self.assertEqual(len(router.routes), 1)


if __name__ == '__main__':
    unittest.main()
