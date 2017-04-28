import asyncio
from sqlalchemy_aio import ASYNCIO_STRATEGY
from sqlalchemy import create_engine
from sqlalchemy.schema import MetaData

from coupon.util import options

options.define('db_host', default='localhost', help='Database hostname or IP address.')
options.define('db_port', default=3306, help='Database port.')
options.define('db_name', default='coupon', help='Database name.')
options.define('db_user', default='username', help='Database username.')
options.define('db_pass', default='password', help='Database password.')

MetaData = MetaData()


class Connection(object):
    _instance = None

    def __new__(cls):
        if not cls._instance:
            engine = create_engine('mysql://{0}:{1}@{2}:{3}/{4}'.format(options.options.db_user,
                                                                        options.options.db_pass,
                                                                        options.options.db_host,
                                                                        options.options.db_port,
                                                                        options.options.db_name),
                                   strategy=ASYNCIO_STRATEGY)
            cls._instance = asyncio.get_event_loop().run_until_complete(engine.connect())
        return cls._instance


async def execute(*args, **kwargs):
    return await Connection().execute(*args, **kwargs)