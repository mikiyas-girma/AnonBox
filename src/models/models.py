from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.orm import sessionmaker, declarative_base
import os

URL = os.getenv('DB_URL')

Base = declarative_base()


class User(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True, index=True)
  telegram_id = Column(BigInteger, unique=True, nullable=False)
  username = Column(String, unique=True, index=True)
  first_name = Column(String)
  last_name = Column(String)


engine = create_engine(URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
