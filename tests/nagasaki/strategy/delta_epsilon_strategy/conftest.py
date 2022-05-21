from decimal import Decimal

import pytest

from nagasaki.clients.bitclude.dto import AccountInfo, Offer, Balance
from nagasaki.models.bitclude import OrderbookRest, OrderbookRestItem, OrderbookRestList
from nagasaki.state import State, DeribitState, BitcludeState


@pytest.fixture(name="initialized_state")
def fixture_initialized_state():
    btc_price_deribit = 40_000
    usd_pln = 4

    top_ask_price = 170_000
    top_ask_amount = 1

    active_plns = 100_000
    active_btcs = 1

    state = State()
    state.deribit = DeribitState()
    state.deribit.btc_mark_usd = Decimal(btc_price_deribit)
    state.usd_pln = Decimal(usd_pln)
    state.bitclude = BitcludeState(
        orderbook_rest=OrderbookRest(
            asks=OrderbookRestList(
                [
                    OrderbookRestItem(
                        price=Decimal(top_ask_price), amount=Decimal(top_ask_amount)
                    )
                ]
            ),
        )
    )
    state.bitclude.account_info = AccountInfo(
        balances={
            "PLN": Balance(active=Decimal(active_plns), inactive=Decimal("0")),
            "BTC": Balance(active=Decimal(active_btcs), inactive=Decimal("0")),
        }
    )
    return state
