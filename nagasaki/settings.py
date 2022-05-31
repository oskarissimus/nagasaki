from functools import cached_property
from pydantic import BaseSettings


class Settings(BaseSettings):
    yahoo_finance_api_key: str = "papaj"
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "example"
    db_name: str = "postgres"
    bitclude_url_base: str = "https://api.bitclude.com"
    bitclude_id: str
    bitclude_key: str
    deribit_url_base: str = "https://www.deribit.com/api/v2"
    deribit_client_id: str
    deribit_client_secret: str

    @cached_property
    def connection_string(self):
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        keep_untouched = (cached_property,)