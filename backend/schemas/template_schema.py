from pydantic import BaseModel


class TemplateCreate(BaseModel):
    name: str
    document_type: str
    markdown_content: str