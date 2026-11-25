from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value

class UserCreate(UserBase):
    password: str = Field(..., min_length=12, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_bcrypt_byte_limit(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes")
        return value

class PasswordResetRequest(UserBase):
    pass

class PasswordResetConfirm(BaseModel):
    token: str = Field(..., min_length=32, max_length=128)
    new_password: str = Field(..., min_length=12, max_length=72)

    @field_validator("new_password")
    @classmethod
    def validate_bcrypt_byte_limit(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes")
        return value

class UserProfileUpdate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(default="", max_length=32)
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(default=None, min_length=12, max_length=72)

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name cannot be blank")
        return value.strip()

    @field_validator("new_password")
    @classmethod
    def validate_password_bytes(cls, value):
        if value is not None and len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 UTF-8 bytes")
        return value

class User(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
