from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.enums.common import MarketEnum
from nagasaki.state import (
    BitcludeState,
    DeribitState,
    OrderbookRest,
    OrderbookWebsocket,
    State,
)
from nagasaki.logger import logger
from nagasaki.clients.usd_pln_quoting_base_client import UsdPlnQuotingBaseClient


class StateInitializer:
    def __init__(
        self,
        bitclude_client: BitcludeClient,
        deribit_client: DeribitClient,
        usd_pln_quoting_client: UsdPlnQuotingBaseClient,
        state: State,
    ):
        self.bitclude_client = bitclude_client
        self.deribit_client = deribit_client
        self.usd_pln_quoting_client = usd_pln_quoting_client
        self.state = state

    def initialize_state(self):
        logger.info("initialize_state")

        self.state.bitclude = BitcludeState()
        self.state.bitclude.orderbook_websocket = OrderbookWebsocket()
        self.state.deribit = DeribitState()

        self.state.bitclude.account_info = self.bitclude_client.fetch_account_info()
        self.state.bitclude.active_offers = self.bitclude_client.fetch_active_offers()
        self.state.deribit.account_summary = self.deribit_client.fetch_account_summary()
        self.state.deribit.mark_price[
            MarketEnum.BTC
        ] = self.deribit_client.fetch_index_price_btc_usd()
        self.state.usd_pln = self.usd_pln_quoting_client.fetch_usd_pln_quote()

        self.state.bitclude.orderbooks[
            MarketEnum.BTC
        ] = self.bitclude_client.fetch_orderbook(MarketEnum.BTC).to_orderbook_rest()

        logger.info(self.state.bitclude.orderbook_rest)
        logger.info(self.state.deribit.mark_price["BTC"])
        logger.info("initialized")
