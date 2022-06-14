import datetime
from decimal import Decimal
from typing import Dict, List, Union

from pydantic import BaseModel, validator

from nagasaki.clients.base_client import OrderMaker
from nagasaki.enums.common import (
    Currency,
    InstrumentTypeEnum,
    MarketEnum,
    Side,
    SideTypeEnum,
    Symbol,
    Type,
)
from nagasaki.models.bitclude import BitcludeOrder, OrderbookRest, OrderbookRestItem
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

    @property
    def btcs(self) -> Decimal:
        return self.btcs_active + self.btcs_inactive

    @property
    def btcs_inactive(self) -> Decimal:
        """w zleceniach"""
        return self.balances["BTC"].inactive

    @property
    def btcs_active(self) -> Decimal:
        """nie są w zleceniach"""
        return self.balances["BTC"].active

    @property
    def plns_inactive(self) -> Decimal:
        """w zleceniach"""
        return self.balances["PLN"].inactive

    @property
    def plns_active(self) -> Decimal:
        """nie są w zleceniach"""
        return self.balances["PLN"].active

    @property
    def plns(self) -> Decimal:
        return self.plns_active + self.plns_inactive


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


class AccountHistory(BaseModel):
    items: List[AccountHistoryItem]


class Offer(BaseModel):
    nr: str
    currency1: Currency
    currency2: Currency
    amount: Decimal
    price: Decimal
    id_user_open: str
    time_open: datetime.datetime
    offertype: SideTypeEnum

    @validator("offertype", pre=True)
    # pylint: disable=no-self-argument,no-self-use
    def convert_to_uppercase(cls, v):
        return v.upper()

    def to_order_maker(self) -> OrderMaker:
        instrument = InstrumentTypeEnum(
            (self.currency1.value.upper(), self.currency2.value.upper())
        )
        return OrderMaker(
            amount=self.amount,
            price=self.price,
            side=self.offertype,
            order_id=self.nr,
            instrument=instrument,
        )


class CreateRequestDTO(BaseModel):
    price: Decimal
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
    def from_order_maker(cls, order: OrderMaker):
        side = Side.BUY if order.side == SideTypeEnum.BID else Side.SELL
        return cls(
            price=order.price,
            symbol=order.symbol,
            type=order.type,
            side=side,
            amount=order.amount,
            params={
                "hidden": order.hidden,
                "post_only": True,
            },
        )

    def to_method_params(self) -> Dict[str, Union[str, Dict[str, int]]]:
        return {
            "price": str(self.price),
            "symbol": self.symbol.value,
            "amount": str(self.amount),
            "type": self.type.value.lower(),
            "side": self.side.value.lower(),
            "params": {
                "hidden": int(self.params["hidden"]),
                "post_only": int(self.params["post_only"]),
            },
        }


class ActionDTO(BaseModel):
    action: Side
    order_id: str

    def __str__(self):
        return f"{self.action.value} order_id: {self.order_id}"


class CreateResponseDTO(BaseModel):
    success: bool
    code: str
    message: str
    actions: ActionDTO

    @validator("actions", pre=True)
    # pylint: disable=no-self-argument,no-self-use
    def fix_actions_structure(cls, v):
        if isinstance(v, dict):
            if "sell" in v:
                return {"action": "SELL", "order_id": v["order"]}
            if "buy" in v:
                return {"action": "BUY", "order_id": v["order"]}
            raise ValueError("Unknown actions structure")
        raise ValueError("actions must be dict")

    def __str__(self):
        return (
            f"success: {self.success}, code: {self.code}, "
            f"message: '{self.message}', actions: ({self.actions})"
        )


class CancelRequestDTO(BaseModel):
    order_id: str
    type: SideTypeEnum

    def get_request_params(self) -> Dict[str, str]:
        return {
            "method": "transactions",
            "action": "cancel",
            "order": self.order_id,
            "typ": self.type.value.lower(),
        }

    def __str__(self):
        return f"order_id: {self.order_id}, type: {self.type}"

    @classmethod
    def from_bitclude_order(cls, order: BitcludeOrder):
        return cls(order_id=order.order_id, type=order.side)

    @classmethod
    def from_order_maker(cls, order: OrderMaker):
        return cls(order_id=order.order_id, type=order.side)


class CancelResponseDTO(BaseModel):
    success: bool
    code: str
    message: str

    def __str__(self):
        return f"success: {self.success}, code: {self.code}, message: {self.message}"


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
