import math


def get_discount_price_ratio(
    btc_mark_price_usd, usd_mark_price_pln, btc_discount_price_pln
):
    mark_pln_price = btc_mark_price_usd * usd_mark_price_pln
    price_delta = mark_pln_price - btc_discount_price_pln
    discount_price_ratio = price_delta / mark_pln_price
    return discount_price_ratio


def get_discount_buy_price_ratio(
    btc_mark_price_usd, usd_mark_price_pln, btc_discount_price_pln
):
    return get_discount_price_ratio(
        btc_mark_price_usd, usd_mark_price_pln, btc_discount_price_pln
    )


def get_discount_sell_price_ratio(
    btc_mark_price_usd, usd_mark_price_pln, btc_discount_price_pln
):
    return -get_discount_price_ratio(
        btc_mark_price_usd, usd_mark_price_pln, btc_discount_price_pln
    )


def round_decimals_down(number: float, decimals: int = 2):
    """
    Returns a value rounded down to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(number)

    factor = 10 ** decimals
    return math.floor(number * factor) / factor
