from sqlalchemy import Column, String, BigInteger
from models.engine.storage import Base


class Question(Base):
    __tablename__ = 'questions'

    question_id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    question = Column(String, nullable=False)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False)
    username = Column(String, nullable=False)
