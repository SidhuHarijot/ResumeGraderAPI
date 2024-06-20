from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from Models.DataModels.User import User

class Create(BaseModel):
    uid: str = Field(..., description="Unique identifier for the user.")
    first_name: str = Field(..., description="First name of the user.")
    last_name: str = Field(..., description="Last name of the user.")
    dob: str = Field(..., description="Date of birth of the user in DDMMYYYY format.")
    phone_number: str = Field(..., description="Phone number of the user. Format: XX-XXXXXXXXXX")
    email: str = Field(..., description="Email of the user.")


class UpdateUser(BaseModel):
    first_name: Optional[str] = Field(None, description="First name of the user.")
    last_name: Optional[str] = Field(None, description="Last name of the user.")
    dob: Optional[str] = Field(None, description="Date of birth of the user in DDMMYYYY format.")
    phone_number: Optional[str] = Field(None, description="Phone number of the user. Format: XX-XXXXXXXXXX")
    email: Optional[str] = Field(None, description="Email of the user.")

