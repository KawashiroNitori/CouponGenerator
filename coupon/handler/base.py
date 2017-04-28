import pytz
import asyncio
import logging
import accept
import calendar
import functools
from aiohttp import web

from coupon import app
from coupon import error
from coupon import template
from coupon.util import json
from coupon.util import options


_logger = logging.getLogger(__name__)


class HandlerBase(object):
    NAME = None
    TITLE = None

    async def prepare(self):
        self.datetime_stamp = _datetime_stamp
        self.reverse_url = _reverse_url

    @property
    def remote_ip(self):
        if options.options.ip_header:
            return self.request.headers.get(options.options.ip_header)
        else:
            return self.request.transport.get_extra_info('peername')[0]

    def render_html(self, template_name, **kwargs):
        kwargs['handler'] = self
        if 'page_name' not in kwargs:
            kwargs['page_name'] = self.NAME
        if 'page_title' not in kwargs:
            kwargs['page_title'] = self.TITLE
        kwargs['reverse_url'] = self.reverse_url
        return template.Environment().get_template(template_name).render(kwargs)

    def render_title(self, page_title=None):
        if not page_title:
            page_title = self.TITLE
        page_title += ' - Coupon'
        return page_title


class Handler(web.View, HandlerBase):
    @asyncio.coroutine
    def __iter__(self):
        try:
            self.response = web.Response()
            yield from HandlerBase.prepare(self)
            yield from super(Handler, self).__iter__()
        except asyncio.CancelledError:
            raise
        except error.UserFacingError as e:
            self.response.set_status(e.http_status, None)
            if self.prefer_json:
                self.response.content_type = 'application/json'
                message = e.message.format(*e.args)
                self.response.text = json.encode({'error': {**e.to_dict(), 'message': message}})
            else:
                self.render(e.template_name, error=e,
                            page_name='error', page_title='Error')
                _logger.warning('User facing error by %s %s: %s', self.url, self.remote_ip, repr(e))
        except:
            _logger.error('System error by %s %s', self.url, self.remote_ip, uid)
            raise
        return self.response

    def render(self, template_name, **kwargs):
        self.response.content_type = 'text/html'
        self.response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.response.headers.add('Pragma', 'no-cache')
        self.response.text = self.render_html(template_name, **kwargs)

    def json(self, obj):
        self.response.content_type = 'application/json'
        self.response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.response.headers.add('Pragma', 'no-cache')
        self.response.text = json.encode(obj)

    async def binary(self, data, type='application/octet-stream'):
        self.response = web.StreamResponse()
        self.response.content_length = len(data)
        self.response.content_type = type
        await self.response.prepare(self.request)
        self.response.write(data)

    @property
    def prefer_json(self):
        for d in accept.parse(self.request.headers.get('Accept')):
            if d.media_type == 'application/json':
                return True
            elif d.media_type == 'text/html' or d.all_types:
                return False
            return False

    @property
    def url(self):
        return self.request.path

    def redirect(self, redirect_url):
        self.response.set_status(web.HTTPFound.status_code, None)
        self.response.headers['Location'] = redirect_url

    def json_or_redirect(self, redirect_url, **kwargs):
        if self.prefer_json:
            self.json(kwargs)
        else:
            self.redirect(redirect_url)

    def json_or_render(self, template_name, **kwargs):
        if self.prefer_json:
            self.json(kwargs)
        else:
            self.render(template_name, **kwargs)


@functools.lru_cache()
def _datetime_stamp(dt):
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=pytz.utc)
    return calendar.timegm(dt.utctimetuple())


@functools.lru_cache()
def _reverse_url(name, **kwargs):
    if kwargs:
        return app.Application().router[name].url(parts=kwargs)
    else:
        return app.Application().router[name].url()


# Decorators

def route_argument(func):
    @functools.wraps(func)
    def wrapped(self, **kwargs):
        return func(self, **kwargs, **self.request.match_info)
    return wrapped


def get_argument(func):
    @functools.wraps(func)
    def wrapped(self, **kwargs):
        return func(self, **kwargs, **self.request.query)
    return wrapped


def post_argument(func):
    @functools.wraps(func)
    async def wrapped(self, **kwargs):
        return await func(self, **kwargs, **await self.request.post())
    return wrapped


def sanitize(func):
    @functools.wraps(func)
    def wrapped(self, **kwargs):
        for key, value in kwargs.items():
            try:
                kwargs[key] = func.__annotations__[key](value)
            except KeyError:
                raise error.UnknownArgumentError(key)
        return func(self, **kwargs)
    return wrapped


