from pydantic import BaseModel, Field, field_validator
from Date import Date

class Experience(BaseModel):
    start_date: Date = Field(..., description="Start date of the experience.")
    end_date: Date = Field(..., description="End date of the experience.")
    title: str = Field(..., description="Title of the experience.")
    company_name: str = Field(..., description="Name of the company.")
    description: str = Field(..., description="Description of the experience.")

