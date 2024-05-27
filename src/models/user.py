from sqlalchemy import Column, Integer, String, BigInteger, ARRAY
from models.engine.storage import Base


class User(Base):
    __tablename__ = 'users'
    telegram_id = Column(BigInteger, primary_key=True, unique=True,
                         nullable=False)
    username = Column(String, unique=True, index=True, default='Anonymous')
    gender = Column(String, default=None)
    bio = Column(String, default=None)
    reputation = Column(Integer, default=0)
    followers = Column(ARRAY(BigInteger), default=[])
    following = Column(ARRAY(BigInteger), default=[])
    date_joined = Column(String)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
