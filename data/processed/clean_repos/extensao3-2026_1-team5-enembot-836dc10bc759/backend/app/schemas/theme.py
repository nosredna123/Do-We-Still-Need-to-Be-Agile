from pydantic import BaseModel, Field

class ThemeSchema(BaseModel):
    id: int
    name: str = Field(max_length=255)