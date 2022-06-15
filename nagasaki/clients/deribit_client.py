from nagasaki.clients.base_client import BaseClient
from nagasaki.clients.bitclude.dto import CreateRequestDTO


class DeribitClient(BaseClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
    ):
        super(DeribitClient, self).__init__(
            "deribit", client_id=client_id, client_secret=client_secret
        )

    def create_order(self, order) -> None:
        self.ccxt_connector.create_order(
            **CreateRequestDTO.from_order_taker(order).to_method_params()
        )
