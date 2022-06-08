from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient
from nagasaki.enums.common import MarketEnum
from nagasaki.logger import logger
from nagasaki.state import State


class StateSynchronizer:
    def __init__(
        self,
        state: State,
        bitclude_client: BitcludeClient,
        deribit_client: DeribitClient,
    ):
        self.state = state
        self.bitclude_client = bitclude_client
        self.deribit_client = deribit_client

    def synchronize_state(self):
        logger.info("Synchronizing state")
        self.state.bitclude.account_info = self.bitclude_client.fetch_account_info()
        self.state.bitclude.active_offers = self.bitclude_client.fetch_active_offers()
        self.state.bitclude.orderbooks[
            MarketEnum.BTC
        ] = self.bitclude_client.fetch_orderbook(MarketEnum.BTC).to_orderbook_rest()
        self.state.deribit.account_summary = self.deribit_client.fetch_account_summary()
