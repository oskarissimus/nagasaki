from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.clients.usd_pln_quoting_base_client import UsdPlnQuotingBaseClient
from nagasaki.logger import logger
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.state import (
    BitcludeState,
    DeribitState,
    OrderbookWebsocket,
    State,
    YahooFinanceState,
)


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

        runtime_config = RuntimeConfig()

        self.state.bitclude = BitcludeState()
        self.state.bitclude.orderbook_websocket = OrderbookWebsocket()
        self.state.deribit = DeribitState()
        self.state.yahoo = YahooFinanceState()

        self.state.bitclude.account_info = self.bitclude_client.fetch_account_info()
        self.state.bitclude.active_offers = self.bitclude_client.fetch_active_offers()
        self.state.deribit.account_summary = self.deribit_client.fetch_account_summary()
        self.state.deribit.mark_price[
            runtime_config.market_making_instrument.market_1
        ] = self.deribit_client.fetch_index_price_in_usd(
            runtime_config.market_making_instrument
        )
        self.state.yahoo.usd_pln = self.usd_pln_quoting_client.fetch_usd_pln_quote()

        self.state.bitclude.orderbooks[
            runtime_config.market_making_instrument.market_1
        ] = self.bitclude_client.fetch_orderbook(
            runtime_config.market_making_instrument.market_1
        ).to_orderbook_rest()

        for orderbook in self.state.bitclude.orderbooks.values():
            logger.info(orderbook)

        logger.info(
            self.state.deribit.mark_price[
                runtime_config.market_making_instrument.market_1
            ]
        )
        logger.info("initialized")
