from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.state import State
from nagasaki.logger import logger


class StateSynchronizer:
    def __init__(self, state: State, bitclude_client: BitcludeClient):
        self.state = state
        self.bitclude_client = bitclude_client

    def synchronize_state(self):
        logger.info("Synchronizing state")
        self.state.bitclude_account_info = self.bitclude_client.fetch_account_info()
        self.state.bitclude_active_offers = self.bitclude_client.fetch_active_offers()
