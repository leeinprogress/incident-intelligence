from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):

    environment: str = "development"

    openai_api_key: str = Field(default="", description="OpenAI API Key")
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature : float = 0.1

    use_mock_data: bool = True

    google_cloud_project: str = Field(default="", description="Google Cloud Project")
    gcp_region: str = "asia-northeast3"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()
