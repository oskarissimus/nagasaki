from decimal import Decimal
from unittest import mock

from nagasaki.enums.common import MarketEnum

from .utils import (
    make_account_info_with_delta_0_002,
    make_order_maker_ask,
    make_orderbook_with_ask,
)


def test_ask_bidding_over_delta(
    bitclude_state, deribit_state, dispatcher, strategy_ask, database
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
    bitclude_state.orderbooks[MarketEnum.BTC] = make_orderbook_with_ask(
        top_ask_price, top_ask_amount
    )
    bitclude_state.account_info = make_account_info_with_delta_0_002()

    strategy_ask.execute()

    expected_create_order = make_order_maker_ask(expected_price, expected_amount)
    dispatcher.dispatch.assert_called_once_with(expected_create_order)
    database.save_order.assert_called_once_with(expected_create_order)
