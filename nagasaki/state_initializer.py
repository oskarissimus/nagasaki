from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.state import State
from nagasaki.clients.coinbase_client import CoinbaseClient
from nagasaki.logger import logger
from nagasaki.clients.usd_pln_quoting_base_client import UsdPlnQuotingBaseClient


class StateInitializer:
    def __init__(
        self,
        bitclude_client: BitcludeClient,
        deribit_client: DeribitClient,
        coinbase_client: CoinbaseClient,
        usd_pln_quoting_client: UsdPlnQuotingBaseClient,
        state: State,
    ):
        self.bitclude_client = bitclude_client
        self.deribit_client = deribit_client
        self.coinbase_client = coinbase_client
        self.usd_pln_quoting_client = usd_pln_quoting_client
        self.state = state

    def initialize_state(self):
        logger.info("initialize_state")
        self.state.bitclude_account_info = self.bitclude_client.fetch_account_info()
        self.state.bitclude_active_offers = self.bitclude_client.fetch_active_offers()
        self.state.btc_mark_usd = self.deribit_client.fetch_index_price_btc_usd()
        self.state.usd_pln = self.usd_pln_quoting_client.fetch_usd_pln_quote()
        ticker = self.bitclude_client.fetch_ticker_btc_pln()
        self.state.ask_orderbook.append(ticker.ask)
        self.state.bid_orderbook.append(ticker.bid)
        logger.info(self.state.ask_orderbook)
        logger.info(self.state.bid_orderbook)
        logger.info(self.state.btc_mark_usd)
        logger.info("initialized")
