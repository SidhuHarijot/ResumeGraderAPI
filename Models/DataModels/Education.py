from pydantic import BaseModel, Field, field_validator
from .Date import Date
import time
from Errors.GetErrors import Errors as e
import regex as re


class Education(BaseModel):
    start_date: Date = Field(..., description="Start date of the education.")
    end_date: Date = Field(..., description="End date of the education.")
    institution: str = Field(..., description="Name of the institution.")
    course_name: str = Field(..., description="Name of the course.")

    @field_validator('start_date')
    def validate_start_date(cls, v, values):
        if v > Date.from_string(time.strftime("%d%m%Y")):
            raise e.ContentInvalid.DateInvalid(v, f"Start date {v} must be before today")
        return v
    
    @field_validator('end_date')
    def validate_end_date(cls, v, values):
        if v < values.data.get("start_date", Date.create("00000000")) and v != Date.create("00000000"):
            raise e.ContentInvalid.DateInvalid(v, f"End date {v} must be after start date {values['start_date']}")
        if v > Date.from_string(time.strftime("%d%m%Y")):
            raise e.ContentInvalid.DateInvalid(v, f"End date {v} must be before today")
        return v
    
    @field_validator('institution')
    def validate_institution(cls, v):
        if re.match(r'[=;]', v):
            raise e.ContentInvalid.InstitutionInvalid(v, "Institution name must contain only letters, numbers and spaces")
        return v

    @field_validator('course_name')
    def validate_course_name(cls, v):
        if re.match(r'[=;]', v):
            raise e.ContentInvalid.TitleInvalid(v, "Course name must contain only letters, numbers and spaces")
        return v

