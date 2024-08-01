from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from .Name import Name
from .Date import Date
from Errors.GetErrors import Errors as e
import regex as re


class User(BaseModel):
    uid: str = Field(..., description="Unique identifier for the user.")
    name: Name = Field(..., description="Name of the user.")
    dob: Date = Field(..., description="Date of birth of the user.")
    is_owner: Optional[bool] = Field(..., description="Whether the user is an owner.")
    is_admin: Optional[bool] = Field(..., description="Whether the user is an admin.")
    phone_number: str = Field(..., description="Phone number of the user. Format: XX-XXXXXXXXXX")
    email: str = Field(..., description="Email of the user.")
    saved_jobs: Optional[List[int]] = Field(..., description="List of job IDs saved by the user.")

    @field_validator('uid')
    def uid_must_be_valid(cls, v):
        if len(v) < 1 or len(v) > 50:
            raise e.ContentInvalid.UIDInvalid(v, "UID must be between 2 and 50 characters")
        if re.match(r'[=;]', v):
            raise e.ContentInvalid.UIDInvalid(v, "UID contains invalid characters")
        return v
    
    @field_validator('phone_number')
    def phone_number_must_be_valid(cls, v):
        if re.match(r'^[0-9]{2}-[0-9]{10}$', v) is None:
            raise e.ContentInvalid.PhoneInvalid(v, "Phone number must be in the format XX-XXXXXXXXXX")
        return v
    
    @field_validator('email')
    def email_must_be_valid(cls, v):
        if len(v) < 5:
            raise e.ContentInvalid.EmailInvalid(v, "Email must be at least 5 characters long")
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v) is None:
            raise e.FormatInvalid.InvalidEmail(v, "Email is not in the correct format")
        return v
    
    @field_validator('saved_jobs')
    def saved_jobs_must_be_valid(cls, v):
        for job_id in v:
            if job_id < 0:
                raise e.ContentInvalid.JobIdInvalid(job_id, "Job ID must be a positive integer")
        return v
