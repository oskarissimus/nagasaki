from decimal import Decimal

from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum
from nagasaki.clients.base_client import OrderMaker
from nagasaki.clients.bitclude.dto import AccountInfo, Balance, Offer
from nagasaki.models.bitclude import OrderbookRest, OrderbookRestItem, OrderbookRestList


def make_offer(price, amount):
    return Offer(
        price=Decimal(price),
        amount=Decimal(amount),
        offertype="ask",
        currency1="btc",
        currency2="pln",
        id_user_open="1337",
        nr="421",
        time_open="2020-01-01T00:00:00Z",
    )


def make_orderbook(price, amount):
    return OrderbookRest(
        asks=OrderbookRestList(
            [OrderbookRestItem(price=Decimal(price), amount=Decimal(amount))]
        )
    )


def make_account_info(active_pln, inactive_pln, active_btc, inactive_btc):
    return AccountInfo(
        balances={
            "PLN": Balance(active=Decimal(active_pln), inactive=Decimal(inactive_pln)),
            "BTC": Balance(active=Decimal(active_btc), inactive=Decimal(inactive_btc)),
        }
    )


def make_order_maker(price, amount):
    return OrderMaker(
        price=price,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PLN,
        side=SideTypeEnum.ASK,
    )
