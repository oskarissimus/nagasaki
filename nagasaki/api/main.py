from dependency_injector.wiring import Provide, inject
from fastapi import Depends, FastAPI

from nagasaki.api.auth import validate_basic_auth
from nagasaki.containers import Application, Strategies
from nagasaki.logger import logger
from nagasaki.runtime_config import RuntimeConfig
from nagasaki.settings.runtime import RuntimeSettings

runtime_config = RuntimeConfig()
app = FastAPI()


@app.get(
    "/runtime-config",
    response_model=RuntimeSettings,
    dependencies=[Depends(validate_basic_auth)],
)
def read_runtime_config():
    return runtime_config.data


@app.post(
    "/runtime-config",
    response_model=RuntimeSettings,
    dependencies=[Depends(validate_basic_auth)],
)
@inject
def update_runtime_config(
    data: RuntimeSettings,
    strategy_container: Strategies = Depends(Provide[Application.strategies]),
):
    with open(runtime_config.path, "w", encoding="utf-8") as file:
        file.write(data.yaml())
    logger.info("Runtime config updated - rebuilding strategies")
    strategy_container.init_resources()
    strategy_container.strategies_provider.reset()
    return data
