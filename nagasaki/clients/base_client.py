import abc
from decimal import Decimal
from typing import Optional

from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum, Symbol, Type
from nagasaki.utils.common import HashableBaseModel


class Order(HashableBaseModel):
    order_id: Optional[str]
    side: SideTypeEnum
    amount: Decimal
    instrument: InstrumentTypeEnum
    hidden: Optional[bool]
    symbol: Optional[Symbol]


class OrderTaker(Order):
    price_limit: Optional[Decimal]
    type: Type = Type.MARKET

    def __repr__(self):
        return (
            f"ORDER - TAKER <{self.side} {self.amount} {self.instrument} "
            f"{self.price_limit} {self.type}>"
        )


class OrderMaker(Order):
    price: Decimal
    type: Type = Type.LIMIT

    def __repr__(self):
        return (
            f"ORDER - MAKER <{self.side} {self.amount} {self.instrument} "
            f"{self.price} {self.type}>"
        )


class BaseClient(abc.ABC):
    @abc.abstractmethod
    def create_order(self, order: Order):
        pass

    @abc.abstractmethod
    def cancel_order(self, order: Order):
        pass
