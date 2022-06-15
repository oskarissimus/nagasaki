from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, Numeric
from sqlalchemy.orm import declarative_base

from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum
from nagasaki.models.bitclude import OrderMaker, OrderTaker

Base = declarative_base()


class OrderMakerDB(Base):
    __tablename__ = "order_maker"

    id = Column(Integer, primary_key=True, index=True)
    side = Column(Enum(SideTypeEnum))
    price = Column(Numeric(precision=20, scale=10))
    amount = Column(Numeric(precision=20, scale=10))
    instrument = Column(Enum(InstrumentTypeEnum))
    time = Column(DateTime, default=datetime.now)

    @classmethod
    def from_order_maker(cls, order: OrderMaker):
        return cls(
            side=order.side,
            price=order.price,
            amount=order.amount,
            instrument=order.instrument,
        )


class OrderTakerDB(Base):
    __tablename__ = "order_taker"

    id = Column(Integer, primary_key=True, index=True)
    side = Column(Enum(SideTypeEnum))
    price_limit = Column(Numeric(precision=20, scale=10), nullable=True)
    amount = Column(Numeric(precision=20, scale=10))
    instrument = Column(Enum(InstrumentTypeEnum))
    time = Column(DateTime, default=datetime.now)

    @classmethod
    def from_order_taker(cls, order: OrderTaker):
        return cls(
            side=order.side,
            price_limit=order.price_limit,
            amount=order.amount,
            instrument=order.instrument,
        )
