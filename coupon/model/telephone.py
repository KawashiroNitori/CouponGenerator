from sqlalchemy.schema import Table, Column
from sqlalchemy.sql import func, select
from sqlalchemy import Integer, String, DateTime, ForeignKey

from coupon import db
from coupon import error

from coupon.model import coupon

Telephone = Table('telephone', db.MetaData,
                  Column('id', Integer, nullable=False, primary_key=True, autoincrement=True),
                  Column('time', DateTime, nullable=False, default=func.now(), index=True),
                  Column('coupon_id', Integer, ForeignKey('coupon.id'), index=True),
                  Column('tel', String(255), nullable=False, index=True))


def add(cid: int, tel: str):
    coupon_res = coupon.get_by_id(cid)
    if not coupon_res:
        raise error.CouponNotFoundError(cid)
    telephone = {'tel': tel,
                 'coupon_id': cid}
    result = db.execute(Telephone.insert().values(**telephone))
    return result.inserted_primary_key
