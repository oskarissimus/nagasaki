from decimal import Decimal

from .utils import (
    make_account_info_with_delta_0_002,
    make_order_maker_ask,
    make_orderbook_with_ask,
)


def test_ask_bidding_over_delta(
    state, bitclude_state, deribit_state, dispatcher, strategy_ask
):
    """
    Total PLN : Total BTC = 1:0 => inventory_parameter = 1 => delta = 0.002
    expected price = btc_mark_usd * usd_pln * (1 + delta)
    """
    btc_mark_usd = 50_000
    expected_price = 200_400
    expected_amount = 1

    top_ask_price = 170_000
    top_ask_amount = 1

    deribit_state.mark_price["BTC"] = Decimal(btc_mark_usd)
    bitclude_state.orderbooks["BTC/PLN"] = make_orderbook_with_ask(
        top_ask_price, top_ask_amount
    )
    bitclude_state.account_info = make_account_info_with_delta_0_002()

    result_order = strategy_ask.execute()

    expected_create_order = make_order_maker_ask(
        Decimal(expected_price), Decimal(expected_amount), hidden=strategy_ask.hidden
    )

    assert result_order == expected_create_order
    dispatcher.dispatch.assert_called_once_with(expected_create_order)
