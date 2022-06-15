from decimal import Decimal

from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum, Symbol
from nagasaki.models.bitclude import OrderTaker


def make_order_taker_sell(amount: Decimal):
    return OrderTaker(
        side=SideTypeEnum.ASK,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PERPETUAL,
        symbol=Symbol.BTC_USD_BTC,
    )


def make_order_taker_buy(amount: Decimal):
    return OrderTaker(
        side=SideTypeEnum.BID,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PERPETUAL,
        symbol=Symbol.BTC_USD_BTC,
    )
