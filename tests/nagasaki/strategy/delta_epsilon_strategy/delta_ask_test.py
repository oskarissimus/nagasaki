from decimal import Decimal
from unittest import mock

from nagasaki.clients.bitclude.dto import AccountInfo, Balance
from nagasaki.enums.common import SideTypeEnum
from nagasaki.state import State
from nagasaki.strategy.delta_epsilon_strategy_ask import DeltaEpsilonStrategyAsk


def test_ask_bidding_over_delta_without_own_orders(initialized_state: State):
    """
    Total PLN : Total BTC = 1:0 => inventory_parameter = 1 => delta = 0.002
    """
    btc_mark_usd = 50_000
    active_pln, inactive_pln = (0, 0)
    active_btc, inactive_btc = (1, 0)
    delta = "0.002"

    state = initialized_state
    state.bitclude.active_offers = []
    state.deribit.btc_mark_usd = Decimal(btc_mark_usd)
    state.bitclude.account_info = AccountInfo(
        balances={
            "PLN": Balance(active=Decimal(active_pln), inactive=Decimal(inactive_pln)),
            "BTC": Balance(active=Decimal(active_btc), inactive=Decimal(inactive_btc)),
        }
    )
    bitclude_client = mock.Mock()

    strategy = DeltaEpsilonStrategyAsk(state, bitclude_client)

    strategy.get_actions()

    bitclude_client.create_order.assert_called_once()
    result_order = bitclude_client.create_order.call_args[0][0]

    delta = Decimal(delta)
    price_to_ask = state.deribit.btc_mark_usd * (Decimal("1") + delta) * state.usd_pln
    assert result_order.side == SideTypeEnum.ASK
    assert result_order.price == price_to_ask
    assert result_order.amount == Decimal("1")
