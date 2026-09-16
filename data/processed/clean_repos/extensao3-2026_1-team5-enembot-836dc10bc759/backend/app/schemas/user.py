from pydantic import BaseModel, EmailStr, Field

class UserSchema(BaseModel):
    id: int
    username: str = Field(max_length=254)
    email: EmailStr = Field(max_length=254)
    password: str = Field(max_length=254)