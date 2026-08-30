from pydantic import BaseModel


class PromptCreate(BaseModel):
    name: str
    content: str

