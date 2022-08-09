from functools import cached_property

from pydantic import BaseSettings


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "example"
    db_name: str = "postgres"

    @cached_property
    def connection_string(self):
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        keep_untouched = (cached_property,)
        env_file = ".env"
