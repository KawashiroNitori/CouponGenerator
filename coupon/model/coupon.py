import shortuuid
from sqlalchemy.schema import Table, Column
from sqlalchemy.sql import func, select
from sqlalchemy import Integer, String, DateTime

from coupon import db

Coupon = Table('coupon', db.MetaData,
               Column('id', Integer, nullable=False, primary_key=True, autoincrement=True),
               Column('time', DateTime, nullable=False, default=func.now(), index=True),
               Column('uuid', String(255), nullable=False, unique=True),
               Column('name', String(255), nullable=False, default=''),
               Column('img', String(255), nullable=False))


async def add(name: str, img: str):
    uuid = shortuuid.uuid()
    coupon = {'uuid': uuid,
              'name': name,
              'img': img}
    await db.execute(Coupon.insert().values(**coupon))
    return uuid


async def get_by_id(cid: int):
    exp = select(Coupon).where(Coupon.c.id == cid)
    result = await db.execute(exp)
    coupon = await result.fetchone()
    return coupon


async def get_by_uuid(uuid: str):
    exp = select(Coupon).where(Coupon.c.uuid == uuid)
    result = await db.execute(exp)
    coupon = await result.fetchone()
    return coupon

