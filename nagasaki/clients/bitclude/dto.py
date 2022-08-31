import datetime as dt
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel, validator

from nagasaki.enums.common import (
    Currency,
    InstrumentTypeEnum,
    MarketEnum,
    Side,
    SideTypeEnum,
    Symbol,
    Type,
)
from nagasaki.models.bitclude import Order, OrderbookRest, OrderbookRestItem
from nagasaki.utils.common import HashableBaseModel, round_decimals_down


class Ticker(BaseModel):
    ask: Decimal
    bid: Decimal


class Balance(BaseModel):
    active: Decimal
    inactive: Decimal


class AccountInfo(BaseModel):
    balances: Dict[str, Balance]

    def assets_total(self, currency: MarketEnum) -> Decimal:
        return self.balances[currency].active + self.balances[currency].inactive


class AccountHistoryItem(HashableBaseModel):
    currency1: str
    currency2: str
    amount: Decimal
    time_close: dt.datetime
    price: Decimal
    fee_taker: int
    fee_maker: int
    type: str
    action: str


class AccountHistory(BaseModel):
    items: List[AccountHistoryItem]


class Offer(BaseModel):
    nr: str
    currency1: Currency
    currency2: Currency
    amount: Decimal
    price: Decimal
    id_user_open: str
    time_open: dt.datetime
    offertype: SideTypeEnum

    @validator("offertype", pre=True)
    # pylint: disable=no-self-argument,no-self-use
    def convert_to_uppercase(cls, v):
        return v.upper()

    def to_order_maker(self) -> Order:
        instrument = InstrumentTypeEnum(
            (self.currency1.value.upper(), self.currency2.value.upper())
        )
        return Order(
            amount=self.amount,
            price=self.price,
            side=self.offertype,
            order_id=self.nr,
            instrument=instrument,
            type=Type.LIMIT,
            post_only=True,
        )

    def __repr__(self) -> str:
        return (
            f"{self.offertype} nr={self.nr} "
            f"date_open={self.time_open.date()} "
            f"time_open={self.time_open.time()} "
            f"{self.currency1}/{self.currency2} "
            f"amount={self.amount:.5f} "
            f"price={self.price:.2f}"
        )

    def __str__(self) -> str:
        return self.__repr__()


class CreateRequestDTO(BaseModel):
    price: Optional[Decimal]
    symbol: Symbol
    type: Type
    side: Side
    amount: Decimal
    params: Dict[str, bool]

    @validator("amount")
    # pylint: disable=no-self-argument,no-self-use
    def validate_amount(cls, v):
        rounded_v = round_decimals_down(v, 4)
        if rounded_v <= 0:
            raise ValueError(
                f"Amount rounded down to 4 decimals must be greater than 0. got {v:.10f}"
            )
        return rounded_v

    def __str__(self):
        return (
            f"{self.side.value} {self.symbol}, "
            f"amount: {self.amount:.10f}, price: {self.price:.2f}, "
            f"params: {self.params}"
        )

    @classmethod
    def from_order(cls, order: Order) -> "CreateRequestDTO":
        side = Side.BUY if order.side == SideTypeEnum.BID else Side.SELL
        return cls(
            price=order.price,
            symbol=order.symbol,
            type=order.type,
            side=side,
            amount=order.amount,
            params={
                "hidden": order.hidden,
                "post_only": order.post_only,
            },
        )

    def to_kwargs(
        self, params_parser: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> Dict[str, Union[str, Dict[str, str]]]:
        return {
            "price": str(self.price) if self.price else None,
            "symbol": self.symbol.value,
            "amount": str(self.amount),
            "type": self.type.value.lower(),
            "side": self.side.value.lower(),
            "params": params_parser(self.params),
        }


class ActionDTO(BaseModel):
    action: Side
    order_id: str

    def __str__(self):
        return f"{self.action.value} order_id: {self.order_id}"


class CancelRequestDTO(BaseModel):
    order_id: str
    side: Side

    def __str__(self):
        return f"order_id: {self.order_id}, side: {self.side}"

    @classmethod
    def from_order(cls, order: Order):
        side = Side.BUY if order.side == SideTypeEnum.BID else Side.SELL
        return cls(order_id=str(order.order_id), side=side)

    def to_method_params(self) -> Dict[str, str]:
        return {"id": self.order_id, "params": {"side": self.side.lower()}}


class OrderbookResponseDTO(BaseModel):
    asks: List[List[Decimal]]
    bids: List[List[Decimal]]
    symbol: Symbol
    timestamp: int

    def to_orderbook_rest(self) -> OrderbookRest:
        asks = [
            OrderbookRestItem(price=price, amount=amount) for price, amount in self.asks
        ]
        bids = [
            OrderbookRestItem(price=price, amount=amount) for price, amount in self.bids
        ]
        return OrderbookRest(asks=asks, bids=bids)


class TradeInfo(BaseModel):
    time: dt.datetime
    nr: str
    amount: Decimal
    price: Decimal
    type: str


class Trade(BaseModel):
    id: str
    timestamp: int
    datetime: dt.datetime
    symbol: str
    side: str
    price: Decimal
    amount: Decimal
    cost: Decimal
    info: TradeInfo
