import datetime
from decimal import Decimal
from typing import Dict, List, Union
from pydantic import BaseModel, validator

from nagasaki.enums.common import (
    OfferCurrencyEnum,
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


# from pydantic import BaseModel
# from typing import List, Dict, Union
# bitclude_market_order_sell_dict = {
#     "success": True,
#     "code": "5053",
#     "actions": {"sell": [], "order": "9400577"},
#     "message": "Order has been submited",
# }


class ActionSellActionsResponseDTO(BaseModel):
    sell: List[str]
    order: str


class ActionBuyActionsResponseDTO(BaseModel):
    buy: List[str]
    order: str


class ActionResponseDTO(BaseModel):
    success: bool
    code: str
    actions: Union[ActionSellActionsResponseDTO, ActionBuyActionsResponseDTO]
    message: str


# a = ActionResponseDTO(**bitclude_market_order_sell_dict)
# print(a.actions.order)
# if isinstance(a.actions, ActionSellActionsResponseDTO):
#     print("sell")
# else:
#     print("buy")
