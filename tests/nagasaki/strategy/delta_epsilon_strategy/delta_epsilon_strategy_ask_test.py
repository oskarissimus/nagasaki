from decimal import Decimal
from unittest import mock

import pytest

from nagasaki.clients.bitclude.dto import AccountInfo, Offer, Balance
from nagasaki.enums.common import ActionTypeEnum, SideTypeEnum
from nagasaki.models.bitclude import OrderbookRest, OrderbookRestItem, OrderbookRestList
from nagasaki.state import State, DeribitState, BitcludeState
from nagasaki.strategy.delta_epsilon_strategy_ask import (
    DeltaEpsilonStrategyAsk,
    calculate_inventory_parameter,
)


@pytest.fixture(name="initialized_state")
def fixture_initialized_state():
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


def test_ask_bidding_over_epsilon_without_own_orders(initialized_state: State):
    state = initialized_state
    state.bitclude.active_offers = []

    bitclude_client = mock.Mock()

    strategy = DeltaEpsilonStrategyAsk(state, bitclude_client)

    top_ask_offer = min(state.bitclude.orderbook_rest.asks, key=lambda x: x.price)
    top_ask = top_ask_offer.price
    epsilon = strategy.epsilon

    strategy.get_actions()

    bitclude_client.create_order.assert_called_once()
    result_order = bitclude_client.create_order.call_args[0][0]

    price_to_ask = top_ask - epsilon
    assert result_order.side == SideTypeEnum.ASK
    assert result_order.price == price_to_ask
    assert result_order.amount == Decimal("1")


@pytest.mark.skip
def test_ask_bidding_over_delta_without_own_orders(initialized_state: State):
    state = initialized_state
    state.bitclude.active_offers = []
    state.deribit.btc_mark_usd = Decimal("50_000")
    strategy = DeltaEpsilonStrategyAsk(state, mock.Mock())

    top_ask_offer = min(state.bitclude.orderbook_rest.asks, key=lambda x: x.price)
    top_ask = top_ask_offer.price
    epsilon = strategy.epsilon

    result_actions = strategy.get_actions()
    price_to_ask = top_ask - epsilon
    assert len(result_actions) == 1
    assert result_actions[0].action_type == ActionTypeEnum.CREATE
    assert result_actions[0].order.side == SideTypeEnum.ASK
    assert result_actions[0].order.price == price_to_ask
    assert result_actions[0].order.amount == Decimal("1")


@pytest.mark.parametrize(
    "total_pln, total_btc, inventory_parameter",
    [
        (100, 0, -1),
        (0, 100, 1),
        (30, 90, 0.5),
        (90, 90, 0),
    ],
)
def test_inventory_parameter(total_pln, total_btc, inventory_parameter):
    assert calculate_inventory_parameter(total_pln, total_btc) == inventory_parameter
