from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum
from nagasaki.models.bitclude import Order

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
    def from_order_maker(cls, order: Order):
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
    def from_order_taker(cls, order: Order):
        return cls(
            side=order.side,
            amount=order.amount,
            instrument=order.instrument,
        )


class BalanceDB(Base):
    __tablename__ = "balance"

    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String)
    amount_active = Column(Numeric(precision=20, scale=10))
    amount_inactive = Column(Numeric(precision=20, scale=10))
    time = Column(DateTime, default=datetime.now)


class Snapshot(Base):
    __tablename__ = "snapshot"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String)
    time = Column(DateTime, default=datetime.now)


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    settings = Column(String)
    time = Column(DateTime, default=datetime.now)


class MyTrades(Base):
    __tablename__ = "my_trades"

    id = Column(Integer, primary_key=True, index=True)
    currency1 = Column(String)
    currency2 = Column(String)
    amount = Column(Numeric(precision=20, scale=10))
    price = Column(Numeric(precision=20, scale=10))
    time_close = Column(DateTime)
    fee_taker = Column(Integer)
    fee_maker = Column(Integer)
    type = Column(String)
    action = Column(String)
