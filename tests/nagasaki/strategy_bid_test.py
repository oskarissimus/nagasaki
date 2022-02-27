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
    bid_to_bidover = 150_000
    own_bid_price = 160_000
    own_bid_amount = 1
    active_plns = 100_000

    state = State()
    state.btc_mark_usd = Decimal(btc_price_deribit)
    state.usd_pln = Decimal(usd_pln)
    state.bid_orderbook = [Decimal(bid_to_bidover)]
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
        )
    ]
    state.bitclude_account_info = AccountInfo(
        balances={"PLN": Balance(active=Decimal(active_plns), inactive=Decimal("0"))}
    )
    return state


def test_bid_bidding_over_epsilon_simple_case(initialized_state: State):
    initialized_state.bitclude_active_offers = []
    bes = BitcludeEpsilonStrategy(initialized_state)

    result_actions = bes.get_actions_bid()

    assert len(result_actions) == 1
    assert result_actions[0].action_type == ActionTypeEnum.CREATE
    assert result_actions[0].order.side == SideTypeEnum.BID
    assert result_actions[0].order.price == Decimal("150_002.137")
    assert result_actions[0].order.amount == Decimal("100_000") / Decimal("150_002.137")


def test_bidding_over_multiple_bids(initialized_state: State):
    initialized_state.bitclude_active_offers = []
    initialized_state.bid_orderbook = [
        Decimal("150_000"),
        Decimal("149_999"),
        Decimal("149_998"),
    ]

    bes = BitcludeEpsilonStrategy(initialized_state)

    result_actions = bes.get_actions_bid()
    assert len(result_actions) == 1
    assert result_actions[0].action_type == ActionTypeEnum.CREATE
    assert result_actions[0].order.side == SideTypeEnum.BID
    assert result_actions[0].order.price == Decimal("150_002.137")
    assert result_actions[0].order.amount == Decimal("100_000") / Decimal("150_002.137")


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


def test_bidding_is_profitable(initialized_state: State):
    bes = BitcludeEpsilonStrategy(initialized_state)
    assert bes.bidding_is_profitable() is True


def test_bidding_is_not_profitable(initialized_state: State):
    initialized_state.btc_mark_usd = Decimal("35_000")
    bes = BitcludeEpsilonStrategy(initialized_state)
    assert bes.bidding_is_profitable() is False
