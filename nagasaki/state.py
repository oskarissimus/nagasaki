from decimal import Decimal
from nagasaki.schemas import BitcludeOrder
from nagasaki.clients.bitclude_client import AccountInfo


class State:
    """
    Modules in python are singletons by default.
    So I created global state that can be accessed by all modules.
    Shame on me.
    I was thinking of using some kind of other pattern, but for now it's fine.
    """

    ask_orderbook = []
    bid_orderbook = []

    # TODO: Seed state with current ticker.

    own_bid: BitcludeOrder = None
    own_ask: BitcludeOrder = None

    bitclude_account_info: AccountInfo = None
    btc_mark_usd: Decimal = None
    usd_pln: Decimal = None

    def get_top_bid(self) -> Decimal:
        return max(self.bid_orderbook)

    def get_top_ask(self) -> Decimal:
        return min(self.ask_orderbook)

    def clear(self):
        self.ask_orderbook = []
        self.bid_orderbook = []
        self.own_ask = None
        self.own_bid = None
        self.bitclude_account_info = None
