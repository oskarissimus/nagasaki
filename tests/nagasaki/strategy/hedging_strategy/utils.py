from decimal import Decimal

from nagasaki.clients.base_client import OrderTaker
from nagasaki.enums.common import SideTypeEnum, InstrumentTypeEnum


def make_order_taker_sell(amount: Decimal):
    return OrderTaker(
        side=SideTypeEnum.ASK,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PERPETUAL,
    )


def make_order_taker_buy(amount: Decimal):
    return OrderTaker(
        side=SideTypeEnum.BID,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PERPETUAL,
    )
