from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from nagasaki.settings import Settings

settings = Settings()
Base = declarative_base()

if settings.memory_db:
    engine = create_engine("sqlite://")
else:
    engine = create_engine(settings.connection_string)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
