from sqlalchemy import Column, BigInteger, String
from models.engine.storage import Base


class State(Base):
    __tablename__ = 'states'

    user_id = Column(BigInteger, primary_key=True)
    question_type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    timeframe = Column(String(50), nullable=False)
