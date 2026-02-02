from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class ModelSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    model_name: str = Field(description="Large language model name", min_length=1)
