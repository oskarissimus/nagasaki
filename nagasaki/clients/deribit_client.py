from nagasaki.clients.base_client import BaseClient


class DeribitClient(BaseClient):
    def __init__(
        self,
        client_key: str,
        client_secret: str,
    ):
        super(DeribitClient, self).__init__(
            "deribit", client_key=client_key, client_secret=client_secret
        )
