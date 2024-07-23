from pydantic import BaseModel, Field, field_validator
from .Date import Date
from Errors.GetErrors import Errors as e
import time
import regex as re

class Experience(BaseModel):
    start_date: Date = Field(..., description="Start date of the experience.")
    end_date: Date = Field(..., description="End date of the experience.")
    title: str = Field(..., description="Title of the experience.")
    company_name: str = Field(..., description="Name of the company.")
    description: str = Field(..., description="Description of the experience.")

    @field_validator('start_date')
    def validate_start_date(cls, v, values):
        if v > Date.from_string(time.strftime("%d%m%Y")):
            raise e.ContentInvalid.DateInvalid(v, f"Start date {v} must be before today")
        return v
    
    @field_validator('end_date')
    def validate_end_date(cls, v, values):
        if v < values.data.get('start_date', Date.create("00000000")) and v != Date.create("00000000"):
            raise e.ContentInvalid.DateInvalid(v, f"End date {v} must be after start date {values['start_date']}")
        if v > Date.from_string(time.strftime("%d%m%Y")):
            raise e.ContentInvalid.DateInvalid(v, f"End date {v} must be before today")
        return v

    @field_validator('title')
    def validate_title(cls, v):
        if len(v) < 2:
            raise e.ContentInvalid.TitleInvalid(v, "Title must be at least 2 characters long")
        if re.match(r'[=;]', v):
            raise e.ContentInvalid.TitleInvalid(v, "Title must contain only letters, numbers and spaces")
        return v
    
    @field_validator('company_name')
    def validate_company_name(cls, v):
        if len(v) < 2:
            raise e.ContentInvalid.EmployerInvalid(v, "Company name must be at least 2 characters long")
        if re.match(r'[=;]', v):
            raise e.ContentInvalid.EmployerInvalid(v, "Company name must contain only letters, numbers and spaces")
        return v
    
    @field_validator('description')
    def validate_description(cls, v):
        if len(v) < 2:
            raise e.ContentInvalid.DescriptionInvalid(v, "Description must be at least 2 characters long")
        if re.match(r'[=;]', v):
            raise e.ContentInvalid.DescriptionInvalid(v, "Description must contain only letters, numbers and spaces")
        return v
