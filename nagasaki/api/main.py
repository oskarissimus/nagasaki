from pathlib import Path
import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic_yaml import YamlModel


class RuntimeConfig:
    class Data(YamlModel):
        papiez: str
        papiez_url: str

    def __init__(self, path: Path):
        self.path = path

    @property
    def data(self):
        return self.Data.parse_raw(self.path.read_text(encoding="utf-8"))

    @property
    def papiez(self):
        return self.data.papiez

    @property
    def papiez_url(self):
        return self.data.papiez_url


runtime_config = RuntimeConfig(
    Path("/home/oskar/git/nagasaki/playground/runtime_config.yml")
)
app = FastAPI()
security = HTTPBasic()


def validate_basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "papa")
    correct_password = secrets.compare_digest(credentials.password, "mobile")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )


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
