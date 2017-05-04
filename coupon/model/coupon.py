import shortuuid
from sqlalchemy.schema import Table, Column
from sqlalchemy.sql import func, select
from sqlalchemy import Integer, String, DateTime
from sqlalchemy_utc import UtcDateTime

from coupon import db

Coupon = Table('coupon', db.MetaData,
               Column('id', Integer, nullable=False, primary_key=True, autoincrement=True),
               Column('time', DateTime, nullable=False, default=func.now(), index=True),
               Column('uuid', String(255), nullable=False, unique=True),
               Column('name', String(255), nullable=False, default=''),
               Column('img', String(255), nullable=False),
               Column('title', String(255), nullable=False, default=''),
               Column('receive_text', String(255), nullable=True, default=None),
               Column('custom_style', String(65535), nullable=True, default=None),
               Column('view_count', Integer, nullable=False, default=0),
               Column('submit_count', Integer, nullable=False, default=0))


def add(img: str, name: str='', title: str='', receive_text: str=None, custom_style: str=None):
    uuid = shortuuid.uuid()
    coupon = {'uuid': uuid,
              'name': name,
              'img': img,
              'title': title,
              'receive_text': receive_text,
              'custom_style': custom_style}
    db.execute(Coupon.insert().values(**coupon))
    return uuid


def edit(cid: str, **kwargs):
    db.execute(Coupon.update().values(**kwargs).where(cid == Coupon.c.uuid))
    return cid


def inc_view(cid: str, value: int=1):
    exp = Coupon.update().values(view_count=Coupon.c.view_count.op('+')(value)).where(Coupon.c.uuid == cid)
    result = db.execute(exp)
    view = result.last_updated_params()
    result.close()
    return view


def inc_submit(cid: str, value: int=1):
    exp = Coupon.update().values(submit_count=Coupon.c.submit_count.op('+')(value)).where(Coupon.c.uuid == cid)
    result = db.execute(exp)
    view = result.last_updated_params()
    result.close()
    return view


def get_by_id(cid: int):
    exp = select([Coupon]).where(Coupon.c.id == cid)
    result = db.execute(exp)
    coupon = result.fetchone()
    result.close()
    return coupon


def get_by_uuid(uuid: str):
    exp = select([Coupon]).where(Coupon.c.uuid == uuid)
    result = db.execute(exp)
    coupon = result.fetchone()
    result.close()
    return coupon


def get_all():
    exp = select([Coupon])
    result = db.execute(exp)
    coupons = result.fetchall()
    result.close()
    return coupons
