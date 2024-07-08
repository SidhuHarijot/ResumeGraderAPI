from pydantic import BaseModel, Field, field_validator
from .Date import Date

class Education(BaseModel):
    start_date: Date = Field(..., description="Start date of the education.")
    end_date: Date = Field(..., description="End date of the education.")
    institution: str = Field(..., description="Name of the institution.")
    course_name: str = Field(..., description="Name of the course.")

