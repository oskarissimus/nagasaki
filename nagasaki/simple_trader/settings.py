from pydantic import BaseSettings


class Settings(BaseSettings):
    bitclude_client_id: str
    bitclude_client_key: str
    deribit_client_id: str
    deribit_client_secret: str
    yahoo_finance_api_key: str

    class Config:
        env_file = ".env"
