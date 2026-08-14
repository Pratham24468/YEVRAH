from pydantic import BaseModel

class CaseCreate(BaseModel):
    title: str
    plaintiff: str
    defendant: str
    facts: str
