from decimal import Decimal

import requests

from nagasaki.clients.usd_pln_quoting_base_client import UsdPlnQuotingBaseClient


# pylint: disable=too-few-public-methods
class TrejdooClient(UsdPlnQuotingBaseClient):
    def fetch_usd_pln_quote(self) -> Decimal:

        endpoint = "http://uat.api.manhattan.trejdoo.com/v1/lmax"
        r = requests.get(endpoint)
        # fmt: off
        buy = [x for x in r.json() if x["lmax_instrument"]["lmax_symbol"] == "USD/PLN"][0]["buy"]
        sell = [x for x in r.json() if x["lmax_instrument"]["lmax_symbol"] == "USD/PLN"][0]["sell"]
        # fmt: on
        mid_price = (buy + sell) / 2
        return Decimal(mid_price)
