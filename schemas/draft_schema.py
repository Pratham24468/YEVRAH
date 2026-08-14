from pydantic import BaseModel

class DraftCreate(BaseModel):
    case_id: int
    document_type: str
    generated_text: str