from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from nagasaki.clients import ExchangeClient
from nagasaki.clients.yahoo_finance.core import YahooFinanceClient
from nagasaki.database import Database
from nagasaki.settings import Settings
from nagasaki.settings.factory import create_strategies
from nagasaki.state import BitcludeState, DeribitState, State, YahooFinanceState


class Clients(
    containers.DeclarativeContainer
):  # pylint: disable=(too-few-public-methods, c-extension-no-member)
    config = providers.Configuration()
    bitclude_client_provider = providers.Singleton(
        ExchangeClient,
        "bitclude",
        client_id=config.bitclude_id,
        client_key=config.bitclude_key,
    )
    deribit_client_provider = providers.Singleton(
        ExchangeClient,
        "deribit",
        client_key=config.deribit_client_id,
        client_secret=config.deribit_client_secret,
    )
    yahoo_finance_client_provider = providers.Singleton(
        YahooFinanceClient,
        api_key=config.yahoo_finance_api_key,
        email=config.yahoo_finance_api_email,
        password=config.yahoo_finance_api_password,
        url_base=config.yahoo_finance_api_url_base,
    )


class States(containers.DeclarativeContainer):
    bitclude_state_provider = providers.Singleton(BitcludeState)
    deribit_state_provider = providers.Singleton(DeribitState)
    yahoo_finance_state_provider = providers.Singleton(YahooFinanceState)

    state_provider = providers.Singleton(State)


class Strategies(containers.DeclarativeContainer):
    clients = providers.DependenciesContainer()
    states = providers.DependenciesContainer()
    databases = providers.DependenciesContainer()

    strategies_provider = providers.Singleton(
        create_strategies,
        database=databases.database_provider,
        state=states.state_provider,
        bitclude_client=clients.bitclude_client_provider,
        deribit_client=clients.deribit_client_provider,
        bitclude_state=states.bitclude_state_provider,
        deribit_state=states.deribit_state_provider,
        yahoo_finance_state=states.yahoo_finance_state_provider,
    )


class Databases(containers.DeclarativeContainer):
    config = providers.Configuration()

    engine_provider = providers.Selector(
        config.db_type,
        memory=providers.Singleton(
            create_engine,
            url="sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=True,
        ),
        postgres=providers.Singleton(
            create_engine,
            providers.Singleton(
                lambda config: f"postgresql://{config['db_user']}:{config['db_password']}@{config['db_host']}:{config['db_port']}/{config['db_name']}",
                config=config,
            ),
        ),
        sqlite_file=providers.Singleton(
            create_engine,
            url="sqlite:///nagasaki.db",
        ),
    )

    session_maker_provider = providers.Singleton(
        sessionmaker, autocommit=False, autoflush=False, bind=engine_provider
    )
    database_provider = providers.Singleton(
        Database, session_maker=session_maker_provider, engine=engine_provider
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[Settings()])

    clients = providers.Container(Clients, config=config)
    states = providers.Container(States)
    databases = providers.Container(Databases, config=config)
    strategies = providers.Container(
        Strategies, clients=clients, states=states, databases=databases
    )
