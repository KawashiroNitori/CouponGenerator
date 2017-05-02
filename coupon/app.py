import logging
import os
from os import path

from aiohttp import web

from coupon.util import options

STATIC_PATH = path.join(path.dirname(__file__), '.static')

options.define('debug', default=False, help='Enable debug mode.')
options.define('ip_header', default='X-Forwarded-For', help='Header name for remote IP.')
options.define('img_static_path', default=path.join(STATIC_PATH, 'img'), help='Static path for storing image.')

_logger = logging.getLogger(__name__)


class Application(web.Application):
    def __init__(self):
        super(Application, self).__init__(debug=options.options.debug)
        globals()[self.__class__.__name__] = lambda: self  # singleton

        from coupon.handler import coupon
        self.router.add_static('/', STATIC_PATH, name='static')
        try:
            os.mkdir(path.join(STATIC_PATH, 'img'))
        except FileExistsError:
            pass


def route(url, name):
    def decorator(handler):
        handler.NAME = handler.NAME or name
        handler.TITLE = handler.TITLE or name
        Application().router.add_route('*', url, handler, name=name)
        return handler
    return decorator
