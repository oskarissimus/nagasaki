from decimal import Decimal

from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum, Symbol, Type
from nagasaki.models.bitclude import Order


def make_order_taker_sell(amount: Decimal):
    return Order(
        side=SideTypeEnum.ASK,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PERPETUAL,
        symbol=Symbol.BTC_USD_BTC,
        hidden=False,
        type=Type.MARKET,
        post_only=False,
    )


def make_order_taker_buy(amount: Decimal):
    return Order(
        side=SideTypeEnum.BID,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PERPETUAL,
        symbol=Symbol.BTC_USD_BTC,
        hidden=False,
        type=Type.MARKET,
        post_only=False,
    )
