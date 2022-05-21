import datetime
from decimal import Decimal
from typing import Dict, List
from pydantic import BaseModel, validator

from nagasaki.clients.base_client import OrderMaker
from nagasaki.enums.common import (
    OfferCurrencyEnum,
    SideTypeEnum,
    MarketEnum,
    ActionEnum,
    InstrumentTypeEnum,
)
from nagasaki.utils.common import round_decimals_down
from nagasaki.models.bitclude import BitcludeOrder, OrderbookRest, OrderbookRestItem

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

    def get_btcs_inactive(self) -> Decimal:
        """w zleceniach"""
        return self.balances["BTC"].inactive

    def get_btcs_active(self) -> Decimal:
        """nie są w zleceniach"""
        return self.balances["BTC"].active

    def get_btcs(self) -> Decimal:
        return self.get_btcs_active() + self.get_btcs_inactive()

    def get_plns_inactive(self) -> Decimal:
        """w zleceniach"""
        return self.balances["PLN"].inactive

    def get_plns_active(self) -> Decimal:
        """nie są w zleceniach"""
        return self.balances["PLN"].active

    def get_plns(self) -> Decimal:
        return self.get_plns_active() + self.get_plns_inactive()


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
    currency1: OfferCurrencyEnum
    currency2: OfferCurrencyEnum
    amount: Decimal
    price: Decimal
    id_user_open: str
    time_open: datetime.datetime
    offertype: SideTypeEnum

    @validator("offertype", pre=True)
    # pylint: disable=no-self-argument,no-self-use
    def convert_to_uppercase(cls, v):
        return v.upper()

    def to_bitclude_order(self) -> BitcludeOrder:
        return BitcludeOrder(
            amount=self.amount,
            price=self.price,
            side=self.offertype,
            order_id=self.nr,
        )

    def to_order_maker(self) -> OrderMaker:
        if (
            self.currency1 == OfferCurrencyEnum.btc
            and self.currency2 == OfferCurrencyEnum.pln
        ):
            instrument = InstrumentTypeEnum.BTC_PLN
        else:
            raise ValueError(
                f"Undefined casting from {self.currency1} and "
                f"{self.currency2} to InstrumentTypeEnum"
            )
        return OrderMaker(
            amount=self.amount,
            price=self.price,
            side=self.offertype,
            order_id=self.nr,
            instrument=instrument,
        )


class CreateRequestDTO(BaseModel):
    action: ActionEnum
    market1: MarketEnum
    market2: MarketEnum
    amount: Decimal
    rate: Decimal
    post_only: bool = True
    hidden: bool = True

    def get_request_params(self) -> Dict[str, str]:
        return {
            "method": "transactions",
            "action": self.action.value.lower(),
            "market1": self.market1.value.lower(),
            "market2": self.market2.value.lower(),
            "amount": str(self.amount),
            "rate": str(self.rate),
            "post_only": int(self.post_only),
            "hidden": int(self.hidden),
        }

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
            f"{self.action.value} {self.market1.value}/{self.market2.value}, "
            f"amount: {self.amount:.10f}, rate: {self.rate:.2f}, "
            f"post_only: {self.post_only}, hidden: {self.hidden}"
        )

    @classmethod
    def from_bitclude_order(cls, order: BitcludeOrder):
        action = ActionEnum.BUY if order.side == SideTypeEnum.BID else ActionEnum.SELL
        return cls(
            action=action,
            market1="BTC",
            market2="PLN",
            amount=order.amount,
            rate=order.price,
        )


class ActionDTO(BaseModel):
    action: ActionEnum
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


class CancelResponseDTO(BaseModel):
    success: bool
    code: str
    message: str

    def __str__(self):
        return f"success: {self.success}, code: {self.code}, message: {self.message}"


class OrderbookResponseDTOData(BaseModel):
    market1: str
    market2: str
    timestamp: int


class OrderbookResponseDTO(BaseModel):
    data: OrderbookResponseDTOData
    bids: List[List[Decimal]]
    asks: List[List[Decimal]]

    def to_orderbook_rest(self) -> OrderbookRest:
        asks = [
            OrderbookRestItem(price=price, amount=amount) for amount, price in self.asks
        ]
        bids = [
            OrderbookRestItem(price=price, amount=amount) for amount, price in self.bids
        ]
        return OrderbookRest(asks=asks, bids=bids)
