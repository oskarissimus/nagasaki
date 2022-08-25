from decimal import Decimal

from nagasaki.clients.bitclude.dto import AccountInfo, Balance, Offer
from nagasaki.enums.common import InstrumentTypeEnum, SideTypeEnum, Symbol, Type
from nagasaki.models.bitclude import (
    Order,
    OrderbookRest,
    OrderbookRestItem,
    OrderbookRestList,
)


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


def make_orderbook_with_ask(price, amount):
    return OrderbookRest(
        asks=OrderbookRestList(
            [OrderbookRestItem(price=Decimal(price), amount=Decimal(amount))]
        )
    )


def make_orderbook_with_bid(price, amount):
    return OrderbookRest(
        bids=OrderbookRestList(
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


def make_order_maker_ask(price: Decimal, amount: Decimal, hidden: bool):
    return Order(
        price=price,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PLN,
        side=SideTypeEnum.ASK,
        hidden=hidden,
        symbol=Symbol.BTC_PLN,
        type=Type.LIMIT,
        post_only=True,
    )


def make_order_maker_bid(price: Decimal, amount: Decimal, hidden: bool):
    return Order(
        price=price,
        amount=amount,
        instrument=InstrumentTypeEnum.BTC_PLN,
        side=SideTypeEnum.BID,
        hidden=hidden,
        symbol=Symbol.BTC_PLN,
        type=Type.LIMIT,
        post_only=True,
    )


def make_account_info_with_delta_0_002():
    active_pln, inactive_pln = (0, 0)
    active_btc, inactive_btc = (1, 0)
    return make_account_info(active_pln, inactive_pln, active_btc, inactive_btc)


def make_account_info_with_delta_0_009():
    active_pln, inactive_pln = (198_200, 0)
    active_btc, inactive_btc = (0, 0)
    return make_account_info(active_pln, inactive_pln, active_btc, inactive_btc)
