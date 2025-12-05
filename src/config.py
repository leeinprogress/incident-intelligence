from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    environment: str = "development"
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
