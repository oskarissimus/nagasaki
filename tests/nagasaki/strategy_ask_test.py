from decimal import Decimal

import pytest

from nagasaki.clients.bitclude.models import AccountInfo, Offer, Balance
from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum
from nagasaki.state import State
from nagasaki.strategy import BitcludeEpsilonStrategy


@pytest.fixture
def initialized_state() -> State:
    btc_price_deribit = 40_000
    usd_pln = 4
    top_bid_orderbook = 150_000
    top_ask_orderbook = 170_000
    own_bid_price = 160_000
    own_ask_price = 200_000
    own_ask_amount = 1
    own_bid_amount = 1
    active_plns = 100_000
    active_btcs = 1

    state = State()
    state.btc_mark_usd = Decimal(btc_price_deribit)
    state.usd_pln = Decimal(usd_pln)
    state.ask_orderbook = [Decimal(top_ask_orderbook)]
    state.bid_orderbook = [Decimal(top_bid_orderbook)]
    state.bitclude_active_offers = [
        Offer(
            price=(own_bid_price),
            amount=Decimal(own_bid_amount),
            offertype="bid",
            currency1="btc",
            currency2="pln",
            id_user_open="1337",
            nr="420",
            time_open="2020-01-01T00:00:00Z",
        ),
        Offer(
            price=(own_ask_price),
            amount=Decimal(own_ask_amount),
            offertype="ask",
            currency1="btc",
            currency2="pln",
            id_user_open="1337",
            nr="421",
            time_open="2020-01-01T00:00:00Z",
        ),
    ]
    state.bitclude_account_info = AccountInfo(
        balances={
            "PLN": Balance(active=Decimal(active_plns), inactive=Decimal("0")),
            "BTC": Balance(active=Decimal(active_btcs), inactive=Decimal("0")),
        }
    )
    return state


def test_ask_bidding_over_epsilon_simple_case(initialized_state: State):
    initialized_state.bitclude_active_offers = []
    bes = BitcludeEpsilonStrategy(initialized_state)

    result_actions = bes.get_actions_ask()

    assert len(result_actions) == 1
    assert result_actions[0].action_type == ActionTypeEnum.CREATE
    assert result_actions[0].order.side == SideTypeEnum.ASK
    assert result_actions[0].order.price == Decimal("170_000") - Decimal("2.137")
    assert result_actions[0].order.amount == Decimal("1")
