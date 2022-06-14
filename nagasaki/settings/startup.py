from functools import cached_property

from pydantic import BaseSettings


class StartupSettings(BaseSettings):
    yahoo_finance_api_key: str = "papaj"
    yahoo_finance_api_email: str = "papaj"
    yahoo_finance_api_password: str = "papaj"
    yahoo_finance_api_url_base: str = "https://yfapi.net"
    db_type: str = "postgres"  # or "memory"
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "example"
    db_name: str = "postgres"
    bitclude_id: str = ""
    bitclude_key: str = ""
    deribit_url_base: str = "https://www.deribit.com/api/v2"
    deribit_client_id: str = ""
    deribit_client_secret: str = ""
    basic_auth_username: str = "papaj"
    basic_auth_password: str = ""

    @cached_property
    def connection_string(self):
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        keep_untouched = (cached_property,)
        env_file = ".env"
