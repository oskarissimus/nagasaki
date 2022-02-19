from decimal import *

from nagasaki.enums import ActionTypeEnum, SideTypeEnum
from nagasaki.schemas import (
    Action,
    BitcludeOrder,
)
from nagasaki.state import State
from nagasaki.strategy import BitcludeEpsilonStrategy

getcontext().prec = 10


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


def test_cancelling_before_bidding():
    state = State()
    state.btc_mark_usd = Decimal("44156")
    state.usd_pln = Decimal("3.87579")
    state.bid_orderbook = [Decimal("169854"), Decimal("169855"), Decimal("169856")]
    bes = BitcludeEpsilonStrategy(state)

    state.own_bid = BitcludeOrder(price=2138, order_id=420, side=SideTypeEnum.BID)
    expected_actions = [
        Action(action_type=ActionTypeEnum.CANCEL, order=state.own_bid),
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


def test_bidding_is_profitable():
    state = State()
    state.btc_mark_usd = Decimal("44156")
    state.usd_pln = Decimal("3.87579")
    state.bid_orderbook = [Decimal("169856")]
    bes = BitcludeEpsilonStrategy(state)
    assert bes.bidding_is_profitable() is True


def test_bidding_is_not_profitable():
    state = State()
    state.btc_mark_usd = Decimal("44156") - Decimal("200")
    state.usd_pln = Decimal("3.87579")
    state.bid_orderbook = [Decimal("169856")]
    bes = BitcludeEpsilonStrategy(state)
    assert bes.bidding_is_profitable() is False
