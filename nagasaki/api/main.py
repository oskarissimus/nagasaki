from dependency_injector.wiring import Provide, inject
from fastapi import Depends, FastAPI

from nagasaki.api.auth import validate_basic_auth
from nagasaki.containers import Application, Strategies
from nagasaki.database.database import Database
from nagasaki.logger import logger
from nagasaki.settings.runtime import RuntimeSettings

app = FastAPI()


@app.get(
    "/runtime-config",
    response_model=RuntimeSettings,
    dependencies=[Depends(validate_basic_auth)],
)
@inject
def read_runtime_config(
    database: Database = Depends(Provide[Application.databases.database_provider]),
):
    return database.get_newest_settings()


@app.post(
    "/runtime-config",
    response_model=RuntimeSettings,
    dependencies=[Depends(validate_basic_auth)],
)
@inject
def update_runtime_config(
    data: RuntimeSettings,
    strategy_container: Strategies = Depends(Provide[Application.strategies]),
    database: Database = Depends(Provide[Application.databases.database_provider]),
):
    database.write_settings_to_db(data)
    logger.info("Runtime config updated - rebuilding strategies")
    strategy_container.init_resources()
    strategy_container.strategies_provider.reset()
    return data
