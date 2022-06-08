from dependency_injector import containers, providers

from nagasaki.clients.bitclude.core import BitcludeClient


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
