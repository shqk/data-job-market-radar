# Load env variable at runtime
from functools import lru_cache
from .models.settings import Settings


# https://fastapi.tiangolo.com/advanced/settings/#creating-the-settings-only-once-with-lru-cache
@lru_cache
def get_settings() -> Settings:
    return Settings()
