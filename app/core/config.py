from pydantic_settings import BaseSettings , SettingsConfigDict
from pydantic import SecretStr
class Settings(BaseSettings):
    DB_URL : str
    SECRET_KEY : SecretStr
    algorithm : str ="HS256"
    access_token_expire_minutes : int = 30
    model_config = SettingsConfigDict(
        env_file = ".env"
    )


settings = Settings()

s= Settings()
