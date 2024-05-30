from datetime import datetime
from sqlalchemy import Column, Date, Integer, String, BigInteger, ARRAY
from models.engine.storage import Base


class User(Base):
    __tablename__ = 'users'
    telegram_id = Column(BigInteger, primary_key=True, unique=True,
                         nullable=False)
    name = Column(String, nullable=False, default='Anonymous')
    username = Column(String, unique=True, index=True)
    gender = Column(String, default=None)
    bio = Column(String, default='You don''t have a bio yet.')
    reputation = Column(Integer, default=0)
    followers = Column(ARRAY(BigInteger), default=[])
    following = Column(ARRAY(BigInteger), default=[])
    date_joined = Column(Date, default=datetime.now().date())
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
