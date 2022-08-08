from nagasaki.clients.base_client import BaseClient
from nagasaki.clients.bitclude.dto import CreateRequestDTO


class DeribitClient(BaseClient):
    def __init__(
        self,
        client_key: str,
        client_secret: str,
    ):
        super(DeribitClient, self).__init__(
            "deribit", client_key=client_key, client_secret=client_secret
        )

    def create_order(self, order) -> None:
        self.ccxt_connector.create_order(
            **CreateRequestDTO.from_order(order).to_kwargs(self.params_parsing_function)
        )
