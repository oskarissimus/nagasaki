from decimal import Decimal
from nagasaki.clients.bitclude_client import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.state import State
from nagasaki.clients.coinbase_client import CoinbaseClient


class StateInitializer:
    def __init__(
        self,
        bitclude_client: BitcludeClient,
        deribit_client: DeribitClient,
        coinbase_client: CoinbaseClient,
        state: State,
    ):
        self.bitclude_client = bitclude_client
        self.deribit_client = deribit_client
        self.coinbase_client = coinbase_client
        self.state = state

    def initialize_state(self):
        self.state.bitclude_account_info = self.bitclude_client.fetch_account_info()
        self.state.bitclude_active_offers = self.bitclude_client.fetch_active_offers()
        self.state.btc_mark_usd = self.deribit_client.fetch_index_price_btc_usd()
        self.state.usd_pln = Decimal(1) / (
            self.coinbase_client.fetch_pln_mark_price_usd()
        )
