from nagasaki.clients.base_client import BaseClient
from nagasaki.logger import logger


class BitcludeClient(BaseClient):
    """
    Client holds ccxt connector and credentials. It makes requests and parses them into models.
    """

    def __init__(
        self,
        client_id: str,
        client_key: str,
    ):
        super(BitcludeClient, self).__init__(
            "bitclude", client_id=client_id, client_key=client_key
        )
