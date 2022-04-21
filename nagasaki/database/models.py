from datetime import datetime
from sqlalchemy import Column, Integer, Enum, Numeric, DateTime

from nagasaki.database.database import Base
from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum
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
