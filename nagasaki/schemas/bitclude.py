from pydantic import BaseModel, validator
from typing import Dict
from decimal import Decimal
import datetime

from nagasaki.enums.common import (
    ActionTypeEnum,
    OfferCurrencyEnum,
    OrderActionEnum,
    SideTypeEnum,
)

# https://github.com/samuelcolvin/pydantic/issues/1303
class HashableBaseModel(BaseModel):
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class Ticker(BaseModel):
    ask: Decimal
    bid: Decimal


class Balance(BaseModel):
    active: Decimal
    inactive: Decimal


class AccountInfo(BaseModel):
    balances: Dict[str, Balance]


class AccountHistoryItem(HashableBaseModel):
    currency1: str
    currency2: str
    amount: Decimal
    time_close: datetime.datetime
    price: Decimal
    fee_taker: int
    fee_maker: int
    type: str
    action: str


class Offer(BaseModel):
    nr: str
    currency1: OfferCurrencyEnum
    currency2: OfferCurrencyEnum
    amount: Decimal
    price: Decimal
    id_user_open: str
    time_open: datetime.datetime
    offertype: SideTypeEnum

    @validator("offertype", pre=True)
    def convert_to_uppercase(cls, v):
        return v.upper()


from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, root_validator, validator


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
    def strip_percent_sign(cls, v):
        return v[:-2]

    @validator("change")
    def convert_percent_to_number(cls, v):
        return v / Decimal(100)

    def __str__(self):
        return f"event_action={self.action} symbol={self.symbol} last={self.last:.10f} volume={self.volume:.10f} change={self.change:.10f}"
