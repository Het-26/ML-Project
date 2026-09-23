from pydantic_settings import BaseSettings, SettingsConfigDict

from app.ml.config import ROOT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", env_file_encoding="utf-8")

    APP_NAME: str = "Churn Prediction API"

    DB_USER: str = "root"
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "churn_db"


settings = Settings()
