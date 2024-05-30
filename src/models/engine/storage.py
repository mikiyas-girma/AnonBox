from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


URL = os.getenv('DB_URL')

engine = create_engine(URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    from models import question, answer, user
    Base.metadata.create_all(bind=engine)
    return engine
