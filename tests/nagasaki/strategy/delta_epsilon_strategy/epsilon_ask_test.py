from decimal import Decimal
from unittest import mock


from nagasaki.state import State
from nagasaki.strategy.delta_epsilon_strategy.ask import (
    DeltaEpsilonStrategyAsk,
    Tolerance,
)
from .utils import (
    make_offer,
    make_orderbook,
    make_order_maker,
)


def test_ask_bidding_over_epsilon_without_own_orders(initialized_state: State):
    top_ask_price = 170_000
    top_ask_amount = 1

    expected_price = "169_999.99"
    expected_amount = 1

    epsilon = Decimal("0.01")

    state = initialized_state
    state.bitclude.active_offers = []
    state.bitclude.orderbook_rest = make_orderbook(top_ask_price, top_ask_amount)

    bitclude_client = mock.Mock()

    strategy = DeltaEpsilonStrategyAsk(state, bitclude_client, epsilon)

    strategy.get_actions()

    expected_create_order = make_order_maker(expected_price, expected_amount)
    bitclude_client.create_order.assert_called_once_with(expected_create_order)


def test_own_order_outside_tolerance_should_cancel_and_create(initialized_state: State):
    top_ask_price = 170_000
    top_ask_amount = 1

    own_ask_price = 200_000
    own_ask_amount = 1

    expected_price = "169_999.99"
    expected_amount = 1

    epsilon = Decimal("0.01")
    tolerance = Tolerance(price=Decimal("100"), amount=Decimal("0.000_3"))

    state = initialized_state
    state.bitclude.active_offers = [make_offer(own_ask_price, own_ask_amount)]
    state.bitclude.orderbook_rest = make_orderbook(top_ask_price, top_ask_amount)

    bitclude_client = mock.Mock()
    strategy = DeltaEpsilonStrategyAsk(state, bitclude_client, epsilon, tolerance)

    strategy.get_actions()

    expected_cancel_order = state.bitclude.active_offers[0].to_order_maker()
    bitclude_client.cancel_and_wait.assert_called_once_with(expected_cancel_order)

    expected_create_order = make_order_maker(expected_price, expected_amount)
    bitclude_client.create_order.assert_called_once_with(expected_create_order)


def test_own_order_inside_tolerance_should_not_cancel_and_create(
    initialized_state: State,
):
    top_ask_price = 170_000
    top_ask_amount = 1

    own_ask_price = "169_999.99"
    own_ask_amount = 1

    epsilon = Decimal("0.01")
    tolerance = Tolerance(price=Decimal("100"), amount=Decimal("0.000_3"))

    state = initialized_state
    state.bitclude.active_offers = [make_offer(own_ask_price, own_ask_amount)]
    state.bitclude.orderbook_rest = make_orderbook(top_ask_price, top_ask_amount)

    bitclude_client = mock.Mock()
    strategy = DeltaEpsilonStrategyAsk(state, bitclude_client, epsilon, tolerance)

    strategy.get_actions()

    bitclude_client.cancel_and_wait.assert_not_called()
    bitclude_client.create_order.assert_not_called()
