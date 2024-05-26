from sqlalchemy import Column, String, BigInteger
from models.engine.storage import Base


class Answer(Base):
    __tablename__ = 'answers'

    answer_id = Column(BigInteger, primary_key=True)
    question_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    answer = Column(String, nullable=False)
    reputation = Column(BigInteger, nullable=False)
    username = Column(String, nullable=False)
