from sqlalchemy import Column, Integer, String, Text
from database import Base

class Draft(Base):
    __tablename__ = "draft"

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer)
    document_type = Column(String)
    generated_text = Column(Text)