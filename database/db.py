from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# from database.config import db_settings

engine = create_engine(
    #"postgresql://hkfnmfvz:BL68E05g2wKT15yo-7qqqn79ms5WhE0S@tiny.db.elephantsql.com/hkfnmfvz"
    # db_settings.SQLALCHEMY_DATABASE_URL
     "sqlite:///./test.db", connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
