from pydantic import BaseModel


class PromptCreate(BaseModel):
    id: int
    name: str
    content: str
    description: str | None = None
