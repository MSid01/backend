from pydantic import BaseSettings


class Database_settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL:str
    
    class Config:
        env_file = ".env"

db_settings = Database_settings()
