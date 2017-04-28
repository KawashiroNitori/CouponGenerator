from os import path

import jinja2
import jinja2.ext
import jinja2.runtime

import coupon
from coupon.util import options


class Undefined(jinja2.runtime.Undefined):
    def __getitem__(self, item):
        return self

    if options.options.debug:
        __str__ = jinja2.runtime.Undefined.__call__


class Environment(jinja2.Environment):
    def __init__(self):
        super(Environment, self).__init__(
            loader=jinja2.FileSystemLoader(path.join(path.dirname(__file__), 'ui/templates')),
            extensions=[jinja2.ext.with_],
            auto_reload=options.options.debug,
            autoescape=True,
            trim_blocks=True,
            undefined=Undefined)
        globals()[self.__class__.__name__] = lambda: self   # singleton

        self.globals['coupon'] = coupon
