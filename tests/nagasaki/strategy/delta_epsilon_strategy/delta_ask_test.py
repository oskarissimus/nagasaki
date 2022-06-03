from decimal import Decimal
from unittest import mock

from nagasaki.state import State
from nagasaki.strategy.calculators.delta_calculator import DeltaCalculator
from nagasaki.strategy.delta_epsilon_strategy.ask import (
    DeltaEpsilonStrategyAsk,
)

from .utils import (
    make_order_maker_ask,
    make_account_info_with_delta_0_002,
    make_orderbook_with_ask,
)


def test_ask_bidding_over_delta(initialized_state: State, dispatcher):
    """
    Total PLN : Total BTC = 1:0 => inventory_parameter = 1 => delta = 0.002
    expected price = btc_mark_usd * usd_pln * (1 + delta)
    """
    btc_mark_usd = 50_000
    expected_price = 200_400
    expected_amount = 1

    top_ask_price = 170_000
    top_ask_amount = 1

    state = initialized_state
    state.deribit.btc_mark_usd = Decimal(btc_mark_usd)
    state.bitclude.orderbook_rest = make_orderbook_with_ask(
        top_ask_price, top_ask_amount
    )
    state.bitclude.account_info = make_account_info_with_delta_0_002()
    delta_calculator = DeltaCalculator(Decimal("0.009"), Decimal("0.002"))

    strategy = DeltaEpsilonStrategyAsk(state, dispatcher)
    strategy.delta_calculator = delta_calculator

    with mock.patch(
        "nagasaki.strategy.market_making_strategy" ".write_order_maker_to_db"
    ):
        strategy.execute()

    expected_create_order = make_order_maker_ask(expected_price, expected_amount)
    dispatcher.dispatch.assert_called_once_with(expected_create_order)
