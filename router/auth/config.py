from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES:int=1
    SECRET_KEY:str 
    ALGORITHM:str
    MAIL_PASSWORD:str
    MAIL_USERNAME: str
    RAPIDAPI_HOST: str
    RAPIDAPI_KEY: str
    FRONT_END_URL: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()


