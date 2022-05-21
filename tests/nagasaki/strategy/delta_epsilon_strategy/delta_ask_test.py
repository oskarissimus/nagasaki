from decimal import Decimal

from nagasaki.state import State
from nagasaki.strategy.delta_epsilon_strategy.ask import (
    DeltaEpsilonStrategyAsk,
)

from .utils import (
    make_account_info,
    make_order_maker,
)


def test_ask_bidding_over_delta(initialized_state: State, dispatcher):
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

    strategy = DeltaEpsilonStrategyAsk(state, dispatcher)

    strategy.get_actions()

    expected_create_order = make_order_maker(expected_price, expected_amount)
    dispatcher.dispatch.assert_called_once_with(expected_create_order)


def make_account_info_with_delta_0_002():
    active_pln, inactive_pln = (0, 0)
    active_btc, inactive_btc = (1, 0)
    return make_account_info(active_pln, inactive_pln, active_btc, inactive_btc)
