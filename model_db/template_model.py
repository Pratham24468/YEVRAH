from sqlalchemy import Column, Integer, String, Text
from database import Base

class Template(Base):
    __tablename__ = "template"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    content  = Column(Text, nullable=False)