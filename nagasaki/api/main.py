from fastapi import Depends, FastAPI

from nagasaki.api.auth import validate_basic_auth
from nagasaki.runtime_config import RuntimeConfig

runtime_config = RuntimeConfig()
app = FastAPI()


@app.get(
    "/runtime-config",
    response_model=RuntimeConfig.Data,
    dependencies=[Depends(validate_basic_auth)],
)
def read_runtime_config():
    return runtime_config.data


@app.post(
    "/runtime-config",
    response_model=RuntimeConfig.Data,
    dependencies=[Depends(validate_basic_auth)],
)
def update_runtime_config(data: RuntimeConfig.Data):
    with open(runtime_config.path, "w", encoding="utf-8") as file:
        file.write(data.yaml())
    return data
