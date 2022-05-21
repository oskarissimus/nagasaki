from decimal import Decimal
from unittest import mock
from unittest.mock import call

from nagasaki.state import State
from nagasaki.strategy.delta_epsilon_strategy_ask import (
    DeltaEpsilonStrategyAsk,
    Tolerance,
)

from .utils import (
    make_account_info,
    make_offer,
    make_orderbook,
    make_order_maker,
)


def test_ask_bidding_over_delta_without_own_orders(initialized_state: State):
    """
    Total PLN : Total BTC = 1:0 => inventory_parameter = 1 => delta = 0.002
    expected price = btc_mark_usd * usd_pln * (1 + delta)
    """
    btc_mark_usd = 50_000
    expected_price = 200_400
    expected_amount = 1

    state = initialized_state
    state.bitclude.active_offers = []
    state.deribit.btc_mark_usd = Decimal(btc_mark_usd)
    state.bitclude.account_info = make_account_info_with_delta_0_002()
    bitclude_client = mock.Mock()

    strategy = DeltaEpsilonStrategyAsk(state, bitclude_client)

    strategy.get_actions()

    expected_create_order = make_order_maker(expected_price, expected_amount)
    bitclude_client.create_order.assert_called_once_with(expected_create_order)


def test_own_order_outside_tolerance_should_cancel_and_create(initialized_state: State):
    """
    Total PLN : Total BTC = 1:0 => inventory_parameter = 1 => delta = 0.002
    expected price = btc_mark_usd * usd_pln * (1 + delta)
    """
    btc_mark_usd = 50_000
    expected_price = 200_400
    expected_amount = 1

    top_ask_price = 170_000
    top_ask_amount = 1

    own_ask_price = 200_000
    own_ask_amount = 1

    epsilon = Decimal("0.01")
    tolerance = Tolerance(price=Decimal("100"), amount=Decimal("0.000_3"))

    state = initialized_state
    state.bitclude.active_offers = [make_offer(own_ask_price, own_ask_amount)]
    state.bitclude.orderbook_rest = make_orderbook(top_ask_price, top_ask_amount)
    state.deribit.btc_mark_usd = Decimal(btc_mark_usd)
    state.bitclude.account_info = make_account_info_with_delta_0_002()

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
    """
    Total PLN : Total BTC = 1:0 => inventory_parameter = 1 => delta = 0.002
    expected price = btc_mark_usd * usd_pln * (1 + delta)
    """
    btc_mark_usd = 50_000

    top_ask_price = 170_000
    top_ask_amount = 1

    own_ask_price = 200_350
    own_ask_amount = 1

    epsilon = Decimal("0.01")
    tolerance = Tolerance(price=Decimal("100"), amount=Decimal("0.000_3"))

    state = initialized_state
    state.bitclude.active_offers = [make_offer(own_ask_price, own_ask_amount)]
    state.bitclude.orderbook_rest = make_orderbook(top_ask_price, top_ask_amount)
    state.deribit.btc_mark_usd = Decimal(btc_mark_usd)
    state.bitclude.account_info = make_account_info_with_delta_0_002()

    bitclude_client = mock.Mock()
    strategy = DeltaEpsilonStrategyAsk(state, bitclude_client, epsilon, tolerance)

    strategy.get_actions()

    bitclude_client.cancel_and_wait.assert_not_called()
    bitclude_client.create_order.assert_not_called()


def test_multiple_own_orders_should_cancel_all_and_create_one(initialized_state: State):
    """
    Total PLN : Total BTC = 1:0 => inventory_parameter = 1 => delta = 0.002
    expected price = btc_mark_usd * usd_pln * (1 + delta)
    """
    btc_mark_usd = 50_000
    expected_price = 200_400
    expected_amount = 1

    top_ask_price = 170_000
    top_ask_amount = 1

    own_ask_price_1 = 200_000
    own_ask_amount_1 = 1

    own_ask_price_2 = 200_300
    own_ask_amount_2 = 1

    epsilon = Decimal("0.01")
    tolerance = Tolerance(price=Decimal("100"), amount=Decimal("0.000_3"))

    state = initialized_state
    state.bitclude.active_offers = [
        make_offer(own_ask_price_1, own_ask_amount_1),
        make_offer(own_ask_price_2, own_ask_amount_2),
    ]
    state.bitclude.orderbook_rest = make_orderbook(top_ask_price, top_ask_amount)
    state.deribit.btc_mark_usd = Decimal(btc_mark_usd)
    state.bitclude.account_info = make_account_info_with_delta_0_002()

    bitclude_client = mock.Mock()
    strategy = DeltaEpsilonStrategyAsk(state, bitclude_client, epsilon, tolerance)

    strategy.get_actions()

    assert bitclude_client.cancel_and_wait.call_count == 2
    expected_cancel_orders = [
        offer.to_order_maker() for offer in state.bitclude.active_offers
    ]
    expected_calls = [call(order) for order in expected_cancel_orders]
    bitclude_client.cancel_and_wait.assert_has_calls(expected_calls, any_order=True)

    expected_create_order = make_order_maker(expected_price, expected_amount)
    bitclude_client.create_order.assert_called_once_with(expected_create_order)


def make_account_info_with_delta_0_002():
    active_pln, inactive_pln = (0, 0)
    active_btc, inactive_btc = (1, 0)
    return make_account_info(active_pln, inactive_pln, active_btc, inactive_btc)
