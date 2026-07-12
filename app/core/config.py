from pydantic_settings import BaseSettings , SettingsConfigDict
from pydantic import SecretStr
class Settings(BaseSettings):
    DB_URL : str
    SECRET_KEY : SecretStr
    OPENAI_API_KEY : str
    GITHUB_ACCESS_TOKEN : str
    
    algorithm : str ="HS256"
    access_token_expire_minutes : int = 30
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
