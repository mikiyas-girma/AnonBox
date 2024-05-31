from sqlalchemy import Column, String, BigInteger
from models.engine.storage import Base


class Question(Base):
    __tablename__ = 'questions'

    question_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    question = Column(String(300), nullable=False)
    category = Column(String(50), nullable=False)
    status = Column(String, nullable=False)
    username = Column(String, nullable=False)
    name = Column(String, nullable=False)
    admin_message_id = Column(BigInteger, nullable=True)
    public_message_id = Column(BigInteger, nullable=True)
