from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Anonimous Confessions"
    API_V1_STR: str = "/v1"
    DATABASE_URL: str
    REDIS_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
