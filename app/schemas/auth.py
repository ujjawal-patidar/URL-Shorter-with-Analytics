from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated
import re


class RegisterRequest(BaseModel):
    name: Annotated[str, Field(..., description="User name")]
    email: Annotated[EmailStr, Field(..., description="User email")]
    password: Annotated[
        str,
        Field(
            ...,
            min_length=8,
            description="Enter a password having min length of 8 characters including atleast one uppercase character, lowercase character, one digit, and one special character",
        ),
    ]

    @field_validator("password")
    def strong_password(cls, password):
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character")
        return password


class LoginRequest(BaseModel):
    email: Annotated[EmailStr, Field(..., description="User Email")]
    password: Annotated[str, Field(min_length=8, description="User password")]
