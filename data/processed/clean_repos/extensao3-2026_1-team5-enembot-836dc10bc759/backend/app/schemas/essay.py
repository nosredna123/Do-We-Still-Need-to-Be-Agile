from pydantic import BaseModel, Field

class EssaySchema(BaseModel):
    id: int
    theme: int
    text: str = Field(max_length=15000)
