from datetime import datetime
from sqlalchemy import Column, Integer, Enum, Numeric, DateTime
from nagasaki.clients.base_client import OrderMaker, OrderTaker

from nagasaki.database.database import Base
from nagasaki.enums.common import ActionTypeEnum, InstrumentTypeEnum, SideTypeEnum
from nagasaki.models.bitclude import Action as BitcludeAction


class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(Enum(ActionTypeEnum))
    order_id = Column(Integer)
    side = Column(Enum(SideTypeEnum))
    price = Column(Numeric(precision=20, scale=10))
    amount = Column(Numeric(precision=20, scale=10))
    time = Column(DateTime)

    @classmethod
    def from_action(cls, action: BitcludeAction):
        return cls(
            action_type=action.action_type,
            order_id=action.order.order_id,
            side=action.order.side,
            price=action.order.price,
            amount=action.order.amount,
            time=datetime.now(),
        )


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
