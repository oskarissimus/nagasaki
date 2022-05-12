from decimal import Decimal

import pytest

from nagasaki.clients.bitclude.dto import AccountInfo, Offer, Balance
from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum
from nagasaki.models.bitclude import OrderbookRest, OrderbookRestItem, OrderbookRestList
from nagasaki.state import State, DeribitState, BitcludeState
from nagasaki.strategy import BitcludeEpsilonStrategy

from hypothesis import assume, given
from hypothesis.strategies import decimals


@pytest.fixture(scope="module")
def initialized_state():
    btc_price_deribit = 40_000
    usd_pln = 4
    top_bid_price = 150_000
    top_ask_price = 170_000
    top_bid_amount = 1
    top_ask_amount = 1
    own_bid_price = 160_000
    own_ask_price = 200_000
    own_ask_amount = 1
    own_bid_amount = 1
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
            bids=OrderbookRestList(
                [
                    OrderbookRestItem(
                        price=Decimal(top_bid_price), amount=Decimal(top_bid_amount)
                    )
                ]
            ),
        )
    )
    state.bitclude.active_offers = [
        Offer(
            price=Decimal(own_bid_price),
            amount=Decimal(own_bid_amount),
            offertype="bid",
            currency1="btc",
            currency2="pln",
            id_user_open="1337",
            nr="420",
            time_open="2020-01-01T00:00:00Z",
        ),
        Offer(
            price=Decimal(own_ask_price),
            amount=Decimal(own_ask_amount),
            offertype="ask",
            currency1="btc",
            currency2="pln",
            id_user_open="1337",
            nr="421",
            time_open="2020-01-01T00:00:00Z",
        ),
    ]
    state.bitclude.account_info = AccountInfo(
        balances={
            "PLN": Balance(active=Decimal(active_plns), inactive=Decimal("0")),
            "BTC": Balance(active=Decimal(active_btcs), inactive=Decimal("0")),
        }
    )
    state.bitclude.active_offers = []
    return state


@given(
    btc_price=decimals(
        allow_nan=False, allow_infinity=False, min_value=160_000, max_value=200_000
    )
)
def test_ask_bidding_over_epsilon_simple_case(initialized_state: State, btc_price):
    initialized_state.bitclude.orderbook_rest.asks = OrderbookRestList(
        [OrderbookRestItem(price=Decimal(btc_price), amount=Decimal(1))]
    )
    bes = BitcludeEpsilonStrategy(initialized_state)
    mark = initialized_state.deribit.btc_mark_usd * initialized_state.usd_pln
    assume((btc_price - mark - bes.EPSILON) / mark > bes.ASK_TRIGGER)

    result_actions = bes.get_actions_ask()
    price_to_ask = btc_price - Decimal("2.137")
    assert len(result_actions) == 1
    assert result_actions[0].action_type == ActionTypeEnum.CREATE
    assert result_actions[0].order.side == SideTypeEnum.ASK
    assert result_actions[0].order.price == price_to_ask
    assert result_actions[0].order.amount == Decimal("1")


@given(
    btc_price=decimals(
        allow_nan=False, allow_infinity=False, min_value=160_000, max_value=200_000
    )
)
def test_ask_bidding_over_epsilon_is_positive(initialized_state: State, btc_price):
    initialized_state.bitclude.orderbook_rest.asks = OrderbookRestList(
        [OrderbookRestItem(price=Decimal(btc_price), amount=Decimal(1))]
    )
    bes = BitcludeEpsilonStrategy(initialized_state)
    mark = initialized_state.deribit.btc_mark_usd * initialized_state.usd_pln
    assume((btc_price - mark - bes.EPSILON) / mark > bes.ASK_TRIGGER)

    result_actions = bes.get_actions_ask()
    assert len(result_actions) == 1
    assert result_actions[0].order.price > 0
