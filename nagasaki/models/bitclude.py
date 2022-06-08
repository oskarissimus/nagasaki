from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, root_validator, validator

from nagasaki.enums.common import ActionTypeEnum, OrderActionEnum, SideTypeEnum


class BitcludeOrder(BaseModel):
    order_id: Optional[int]
    side: SideTypeEnum
    price: Decimal
    amount: Decimal

    def __str__(self):
        return f"ORDER <{self.side} {self.price} {self.amount}>"

    def __repr__(self):
        return f"ORDER <{self.side} {self.price} {self.amount}>"


class Action(BaseModel):
    action_type: ActionTypeEnum
    order: Optional[BitcludeOrder]

    def __str__(self):
        return f"ACTION <{self.action_type} {self.order}>"

    def __repr__(self):
        return f"ACTION <{self.action_type} {self.order}>"


class BitcludeEventBase(BaseModel):
    action: str
    symbol: str


class BitcludeEventOrderbook(BitcludeEventBase):
    size: Decimal
    price: Decimal
    side: str
    order_action: Optional[OrderActionEnum]

    @root_validator()
    # pylint: disable=no-self-argument,no-self-use
    def infer_order_action_based_on_value(cls, values):
        if values["size"] == Decimal(0):
            values["order_action"] = OrderActionEnum.CANCELLED
        else:
            values["order_action"] = OrderActionEnum.CREATED
        return values

    def __str__(self):
        return f"event_action={self.action} symbol={self.symbol} side={self.side} price={self.price} size={self.size:.10f} order_action={self.order_action}"


class BitcludeEventTicker(BitcludeEventBase):
    last: Decimal
    volume: Decimal
    change: Decimal

    @validator("change", pre=True)
    # pylint: disable=no-self-argument,no-self-use
    def strip_percent_sign(cls, v):
        return v[:-2]

    @validator("change")
    # pylint: disable=no-self-argument,no-self-use
    def convert_percent_to_number(cls, v):
        return v / Decimal(100)

    def __str__(self):
        return f"event_action={self.action} symbol={self.symbol} last={self.last:.10f} volume={self.volume:.10f} change={self.change:.10f}"


class OrderbookWebsocketList(List[Decimal]):
    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        ret = ""
        for offer in self:
            ret += f"{offer} "
        return ret


class OrderbookRestItem(BaseModel):
    price: Decimal
    amount: Decimal

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"[{self.price:.2f} {self.amount:.8f}]"


class OrderbookRestList(List[OrderbookRestItem]):
    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        ret = ""
        for offer in self:
            ret += f"{offer} "
        return ret


class OrderbookWebsocket(BaseModel):
    asks: Optional[OrderbookWebsocketList]
    bids: Optional[OrderbookWebsocketList]


class OrderbookRest(BaseModel):
    asks: Optional[OrderbookRestList]
    bids: Optional[OrderbookRestList]
