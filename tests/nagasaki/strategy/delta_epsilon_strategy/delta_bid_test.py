from decimal import Decimal

from .utils import (
    make_account_info_with_delta_0_009,
    make_order_maker_bid,
    make_orderbook_with_bid,
)


def test_bid_bidding_over_delta(
    dispatcher, strategy_bid, bitclude_state, deribit_state
):
    """
    Total PLN : Total BTC = 1:0 => inventory_parameter = 1 => delta = 0.002
    expected price = btc_mark_usd * usd_pln * (1 - delta)
    """
    btc_mark_usd = 50_000
    expected_price = 198_200
    expected_amount = 1

    top_bid_price = 199_000
    top_bid_amount = 1

    bitclude_state.orderbooks["BTC/PLN"] = make_orderbook_with_bid(
        top_bid_price, top_bid_amount
    )
    deribit_state.mark_price["BTC"] = Decimal(btc_mark_usd)
    bitclude_state.account_info = make_account_info_with_delta_0_009()

    result_order = strategy_bid.execute()

    expected_create_order = make_order_maker_bid(
        expected_price, expected_amount, strategy_bid.hidden
    )

    assert result_order == expected_create_order
    dispatcher.dispatch.assert_called_once_with(expected_create_order)
