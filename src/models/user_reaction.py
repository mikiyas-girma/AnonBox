from sqlalchemy import Column, Integer, String, BigInteger, UniqueConstraint
from models.engine.storage import Base


class UserReaction(Base):
    __tablename__ = 'user_reactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    answer_id = Column(BigInteger)
    reaction_type = Column(String)

    __table_args__ = (UniqueConstraint('user_id', 'answer_id', name='_user_answer_uc'),)
