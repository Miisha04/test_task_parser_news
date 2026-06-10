
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_user: str = Field(validation_alias="DB_USER")
    db_password: str = Field(validation_alias="DB_PASSWORD")
    db_name: str = Field(validation_alias="DB_NAME")
    db_host: str = Field(validation_alias="DB_HOST")
    db_port: int = Field(validation_alias="DB_PORT")

    ria_news_url: str = Field(
        validation_alias="RIA_NEWS_URL", 
        default="https://ria.ru"
    )

    @field_validator("db_user")
    @classmethod
    def _validate_db_user(cls, v: str):
        if not v:
            raise ValueError("DB_USER cant be None")
        return v
        
    @field_validator("db_password")
    @classmethod
    def _validate_db_password(cls, v: str):
        if not v:
            raise ValueError("DB_PASSWORD cant be None")
        return v
        
    @field_validator("db_host")
    @classmethod
    def _validate_db_host(cls, v: str):
        if not v:
            raise ValueError("DB_HOST cant be None")
        return v
        
    @field_validator("db_port")
    @classmethod
    def _validate_db_port(cls, v: int):
        if not v:
            raise ValueError("DB_PORT cant be None")
        return v
        
    @field_validator("db_name")
    @classmethod
    def _validate_db_name(cls, v: str):
        if not v:
            raise ValueError("DB_NAME cant be None")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


