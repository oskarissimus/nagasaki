from decimal import Decimal

import pytest
from hypothesis import given, assume
from hypothesis.strategies import decimals

from nagasaki.clients.bitclude.dto import AccountInfo, Offer, Balance
from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum
from nagasaki.models.bitclude import OrderbookRestList, OrderbookRestItem, OrderbookRest
from nagasaki.state import State, DeribitState, BitcludeState
from nagasaki.strategy import BitcludeEpsilonStrategy


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


def test_bid_bidding_over_epsilon_simple_case(initialized_state: State):
    """
    btc_price is variable used by hypothesis to inject different prices and check for counterexamples
    """
    initialized_state.bitclude.orderbook_rest.bids = OrderbookRestList(
        [OrderbookRestItem(price=Decimal(150_000), amount=Decimal(1))]
    )
    bes = BitcludeEpsilonStrategy(initialized_state)

    result_actions = bes.get_actions_bid()

    assert len(result_actions) == 1
    assert result_actions[0].action_type == ActionTypeEnum.CREATE
    assert result_actions[0].order.side == SideTypeEnum.BID
    assert result_actions[0].order.price == Decimal("150_002.137")
    assert result_actions[0].order.amount == Decimal("100_000") / Decimal("150_002.137")


def test_bidding_over_multiple_bids(initialized_state: State):
    initialized_state.bitclude.orderbook_rest.bids = OrderbookRestList(
        [OrderbookRestItem(price=Decimal(150_000), amount=Decimal(1)),
         OrderbookRestItem(price=Decimal(149_999), amount=Decimal(1)),
         OrderbookRestItem(price=Decimal(149_998), amount=Decimal(1))
         ]
    )

    bes = BitcludeEpsilonStrategy(initialized_state)

    result_actions = bes.get_actions_bid()
    assert len(result_actions) == 1
    assert result_actions[0].action_type == ActionTypeEnum.CREATE
    assert result_actions[0].order.side == SideTypeEnum.BID
    assert result_actions[0].order.price == Decimal("150_002.137")
    assert result_actions[0].order.amount == Decimal("100_000") / Decimal("150_002.137")


@pytest.mark.skip("Not implemented")
def test_cancelling_before_bidding(initialized_state: State):
    bes = BitcludeEpsilonStrategy(initialized_state)

    result_actions = bes.get_actions_bid()
    assert len(result_actions) == 2

    assert result_actions[0].action_type == ActionTypeEnum.CANCEL
    assert result_actions[0].order.side == SideTypeEnum.BID
    assert result_actions[0].order.price == Decimal("160_000")
    assert result_actions[0].order.amount == Decimal("1")

    assert result_actions[1].action_type == ActionTypeEnum.CREATE
    assert result_actions[1].order.side == SideTypeEnum.BID
    assert result_actions[1].order.price == Decimal("150_002.137")
    assert result_actions[1].order.amount == Decimal("100_000") / Decimal("150_002.137")


@pytest.mark.skip("Not implemented")
def test_bidding_is_profitable(initialized_state: State):
    bes = BitcludeEpsilonStrategy(initialized_state)
    assert bes.bidding_is_profitable() is True


@pytest.mark.skip("Not implemented")
def test_bidding_is_not_profitable(initialized_state: State):
    initialized_state.btc_mark_usd = Decimal("35_000")
    bes = BitcludeEpsilonStrategy(initialized_state)
    assert bes.bidding_is_profitable() is False
