from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):

    environment: str = "development"

    openai_api_key: str = Field(..., description="OpenAI API Key")
    openai_model: str = "gpt-4-turbo-preview"
    openai_temperature : float = 0.1

    use_mock_data: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
