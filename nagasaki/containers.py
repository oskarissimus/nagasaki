from dependency_injector import containers, providers

from nagasaki.clients.bitclude.core import BitcludeClient
from nagasaki.clients.deribit_client import DeribitClient


class Clients(
    containers.DeclarativeContainer
):  # pylint: disable=(too-few-public-methods, c-extension-no-member)
    config = providers.Configuration()
    bitclude_client = providers.Singleton(
        BitcludeClient,
        bitclude_url_base=config.bitclude_url_base,
        bitclude_client_id=config.bitclude_id,
        bitclude_client_key=config.bitclude_key,
    )
    deribit_client = providers.Singleton(
        DeribitClient,
        deribit_url_base=config.deribit_url_base,
        deribit_client_id=config.deribit_client_id,
        deribit_client_secret=config.deribit_client_secret,
    )
