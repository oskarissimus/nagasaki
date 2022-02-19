from decimal import Decimal
from nagasaki.clients.bitclude_client import Offer

from nagasaki.enums import ActionTypeEnum, SideTypeEnum
from nagasaki.schemas import (
    Action,
    BitcludeOrder,
)
from nagasaki.state import State
from nagasaki.strategy import BitcludeEpsilonStrategy
import pytest


def test_bidding_over_epsilon_simple_case():
    state = State()
    bes = BitcludeEpsilonStrategy(state)
    state.btc_mark_usd = Decimal("44156")
    state.usd_pln = Decimal("3.87579")
    state.bid_orderbook = [Decimal("169856")]
    state.own_bid = None

    expected_actions = [
        Action(
            action_type=ActionTypeEnum.CREATE,
            order=BitcludeOrder(
                side=SideTypeEnum.BID,
                price=(Decimal("169856") + Decimal("2.137")),
            ),
        )
    ]
    result_actions = bes.get_actions_bid()
    assert expected_actions == result_actions


def test_bidding_over_multiple_bids():
    state = State()
    state.btc_mark_usd = Decimal("44156")
    state.usd_pln = Decimal("3.87579")
    state.bid_orderbook = [Decimal("169854"), Decimal("169855"), Decimal("169856")]
    state.own_bid = None
    bes = BitcludeEpsilonStrategy(state)

    expected_actions = [
        Action(
            action_type=ActionTypeEnum.CREATE,
            order=BitcludeOrder(
                side=SideTypeEnum.BID,
                price=(Decimal("169856") + Decimal("2.137")),
            ),
        )
    ]
    result_actions = bes.get_actions_bid()
    assert expected_actions == result_actions


@pytest.fixture
def initialized_state() -> State:
    state = State()
    state.btc_mark_usd = Decimal("44156")
    state.usd_pln = Decimal("3.87579")
    state.bid_orderbook = [Decimal("169856")]
    state.bitclude_active_offers = [
        Offer(
            price=Decimal("2138"),
            amount=Decimal("0.1"),
            nr="420",
            offertype="bid",
            currency1="btc",
            currency2="pln",
            id_user_open="1337",
            time_open="2020-01-01T00:00:00Z",
        )
    ]
    return state


def test_cancelling_before_bidding(initialized_state: State):
    initialized_state.bid_orderbook = [
        Decimal("169854"),
        Decimal("169855"),
        Decimal("169856"),
    ]
    bes = BitcludeEpsilonStrategy(initialized_state)

    own_bid = BitcludeOrder(
        side=SideTypeEnum.BID,
        price=Decimal("2138"),
        order_id=420,
    )
    expected_actions = [
        Action(action_type=ActionTypeEnum.CANCEL, order=own_bid),
        Action(
            action_type=ActionTypeEnum.CREATE,
            order=BitcludeOrder(
                side=SideTypeEnum.BID,
                price=(Decimal("169856") + Decimal("2.137")),
            ),
        ),
    ]
    result_actions = bes.get_actions_bid()
    assert expected_actions == result_actions


def test_bidding_is_profitable(initialized_state: State):
    bes = BitcludeEpsilonStrategy(initialized_state)
    assert bes.bidding_is_profitable() is True


def test_bidding_is_not_profitable(initialized_state: State):
    initialized_state.btc_mark_usd = Decimal("44156") - Decimal("200")
    bes = BitcludeEpsilonStrategy(initialized_state)
    assert bes.bidding_is_profitable() is False
