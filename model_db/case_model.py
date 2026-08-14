from sqlalchemy import Column, Integer, String, Text
from database import Base

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    plaintiff = Column(String)
    defendant = Column(String)
    facts = Column(Text)