from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    db_name: str = "civicreach"
    default_radius_meters: int = 5000
    max_radius_meters: int = 50000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
