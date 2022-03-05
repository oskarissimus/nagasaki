from decimal import Decimal
import requests


def get_price_usd_pln() -> Decimal:

    endpoint = "http://uat.api.manhattan.trejdoo.com/v1/lmax"
    r = requests.get(endpoint)
    buy = [x for x in r.json() if x["lmax_instrument"]["lmax_symbol"] == "USD/PLN"][0][
        "buy"
    ]
    sell = [x for x in r.json() if x["lmax_instrument"]["lmax_symbol"] == "USD/PLN"][0][
        "sell"
    ]
    mid_price = (buy + sell) / 2
    return Decimal(mid_price)
