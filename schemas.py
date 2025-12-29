from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    full_name: str

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str
    message: str

class UserResponse(BaseModel):
    """Schema for user response (no password!)"""
    id: int
    email: str
    username: str
    full_name: str
    is_active: bool
    
    class Config:
        from_attributes = True