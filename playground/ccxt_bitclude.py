import ccxt
import ccxt_unmerged  # pylint: disable=unused-import
import pytest

BITCLUDE_ID = "xxx"
BITCLUDE_KEY = "xxx"

exchange = getattr(ccxt, "bitclude")
client = exchange({"apiKey": BITCLUDE_KEY, "uid": BITCLUDE_ID})


@pytest.mark.parametrize(
    "post_only, expected_error",
    [
        # this creates order but also raises error, it propably should be InvalidOrder
        (True, ccxt.errors.RequestTimeout),
        # this is proper way to pass post_only, it propably should be OrderImmediatelyFillable
        (1, ccxt.errors.ExchangeError),
        # this is proper way to pass post_only, it propably should be OrderImmediatelyFillable
        ("1", ccxt.errors.ExchangeError),
    ],
)
def test_create_order_post_only_error(post_only, expected_error):
    with pytest.raises(expected_error):
        client.create_order(
            price="0.50",
            symbol="XRP/PLN",
            amount=1,
            type="limit",
            side="sell",
            params={"post_only": post_only},
        )
