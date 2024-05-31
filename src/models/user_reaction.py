from sqlalchemy import Column, Integer, String, BigInteger
from models.engine.storage import Base


class UserReaction(Base):
    __tablename__ = 'user_reactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    answer_id = Column(BigInteger)
    reaction_type = Column(String)
