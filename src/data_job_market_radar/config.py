# Load env variable at runtime
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    client_id: str = Field(validation_alias="FRANCE_TRAVAIL_CLIENT_ID")
    client_secret: str = Field(validation_alias="FRANCE_TRAVAIL_CLIENT_SECRET")
    token_url: str = Field(validation_alias="FRANCE_TRAVAIL_TOKEN_URL")
    search_url: str = Field(validation_alias="FRANCE_TRAVAIL_SEARCH_URL")
    scope: str = Field(validation_alias="FRANCE_TRAVAIL_SCOPE")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# https://fastapi.tiangolo.com/advanced/settings/#creating-the-settings-only-once-with-lru-cache
@lru_cache
def get_settings() -> Settings:
    return Settings()