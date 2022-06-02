from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from nagasaki.settings import Settings

Base = declarative_base()
SessionLocal = None  # pylint: disable=invalid-name
engine = None  # pylint: disable=invalid-name


def init_db():
    settings = Settings()

    global engine  # pylint: disable=(global-statement, invalid-name)
    if settings.memory_db:
        engine = create_engine("sqlite://")
    else:
        engine = create_engine(settings.connection_string)

    global SessionLocal  # pylint: disable=(global-statement, invalid-name)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
