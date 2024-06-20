from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from Name import Name
from Date import Date


class User(BaseModel):
    uid: str = Field(..., description="Unique identifier for the user.")
    name: Name = Field(..., description="Name of the user.")
    dob: Date = Field(..., description="Date of birth of the user.")
    is_owner: Optional[bool] = Field(..., description="Whether the user is an owner.")
    is_admin: Optional[bool] = Field(..., description="Whether the user is an admin.")
    phone_number: str = Field(..., description="Phone number of the user. Format: XX-XXXXXXXXXX")
    email: str = Field(..., description="Email of the user.")
