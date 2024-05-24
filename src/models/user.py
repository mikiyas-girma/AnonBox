from sqlalchemy import Column, Integer, String, BigInteger
from models.engine.storage import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
