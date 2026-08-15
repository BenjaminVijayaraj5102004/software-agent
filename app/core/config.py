import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    DB_URL: str
    SECRET_KEY: SecretStr
    GITHUB_ACCESS_TOKEN: str | None = None
    NVIDIA_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    # LangSmith tracing settings
    LANGSMITH_TRACING: bool = True
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_PROJECT: str = "software-agent"

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cli_access_token_expire_hours: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def setup_langsmith_environment(self) -> None:
        """Configures environment variables for LangSmith tracing across agents."""
        if self.LANGSMITH_TRACING:
            os.environ["LANGSMITH_TRACING"] = str(self.LANGSMITH_TRACING).lower()
            os.environ["LANGSMITH_ENDPOINT"] = self.LANGSMITH_ENDPOINT
            if self.LANGSMITH_API_KEY:
                os.environ["LANGSMITH_API_KEY"] = self.LANGSMITH_API_KEY
                os.environ["LANGCHAIN_API_KEY"] = self.LANGSMITH_API_KEY
            if self.LANGSMITH_PROJECT:
                os.environ["LANGSMITH_PROJECT"] = self.LANGSMITH_PROJECT
                os.environ["LANGCHAIN_PROJECT"] = self.LANGSMITH_PROJECT
            os.environ["LANGCHAIN_TRACING_V2"] = str(self.LANGSMITH_TRACING).lower()
            os.environ["LANGCHAIN_ENDPOINT"] = self.LANGSMITH_ENDPOINT


settings = Settings()
settings.setup_langsmith_environment()

