from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import re


NAME_PATTERN = re.compile(r'^.*[A-Za-z]+.*-\s+$', re.IGNORECASE)



class Date(BaseModel):
    day: int = Field(..., description="Day of the date.")
    month: int = Field(..., description="Month of the date.")
    year: int = Field(..., description="Year of the date.")

    @field_validator('day')
    def day_must_be_valid(cls, v):
        if v == 0:
            return v
        if v < 1 or v > 31:
            raise ValueError('Day must be between 1 and 31')
        return v

    @field_validator('month')
    def month_must_be_valid(cls, v):
        if v == 0:
            return v
        if v < 1 or v > 12:
            raise ValueError('Month must be between 1 and 12')
        return v

    @field_validator('year')
    def year_must_be_valid(cls, v):
        if v < 0 or v > 9999:
            raise ValueError('Year must be between 0 and 9999')
        return v

    def __str__(self):
        return f"{self.day:02d}{self.month:02d}{self.year:04d}"
    
    @classmethod
    def from_string(cls, date_str: str):
        if len(date_str) != 8:
            raise ValueError("Date string must be in DDMMYYYY format")
        day = int(date_str[:2])
        month = int(date_str[2:4])
        year = int(date_str[4:])
        return cls(day=day, month=month, year=year)

class Name(BaseModel):
    first_name: str = Field(..., description="First name of the user.")
    last_name: str = Field(..., description="Last name of the user.")

    @field_validator('first_name')
    def first_name_must_be_valid(cls, v):
        if len(v) < 2 or len(v) > 50:
            raise ValueError('First name must be between 2 and 50 characters')
        if not NAME_PATTERN.match(v):
            raise ValueError('First name contains invalid characters')
        return v
    
    @field_validator('last_name')
    def last_name_must_be_valid(cls, v):
        if len(v) < 2 or len(v) > 50:
            raise ValueError('Last name must be between 2 and 50 characters')
        if not NAME_PATTERN.match(v):
            raise ValueError('Last name contains invalid characters')
        return v
    
    def __str__(self):
        return f"[({self.first_name}), ({self.last_name})]"
    
    @classmethod
    def from_string(cls, name_str: str):
        if len(name_str) < 2 or len(name_str) > 100:
            raise ValueError("Name string must be between 2 and 100 characters")
        first_name = name_str[2: name_str.index(')')]
        last_name = name_str[name_str.index('(', 2) + 1: -2]
        return cls(first_name=first_name, last_name=last_name)

class Experience(BaseModel):
    start_date: Date = Field(..., description="Start date of the experience.")
    end_date: Date = Field(..., description="End date of the experience.")
    title: str = Field(..., description="Title of the experience.")
    company_name: str = Field(..., description="Name of the company.")
    description: str = Field(..., description="Description of the experience.")

class Education(BaseModel):
    start_date: Date = Field(..., description="Start date of the education.")
    end_date: Date = Field(..., description="End date of the education.")
    institution: str = Field(..., description="Name of the institution.")
    course_name: str = Field(..., description="Name of the course.")

class Resume(BaseModel):
    uid: str = Field(..., description="User ID associated with the resume.")
    skills: List[str] = Field(..., description="List of skills.")
    experience: List[Experience] = Field(..., description="List of experiences.")
    education: List[Education] = Field(..., description="List of education records.")

class Job(BaseModel):
    job_id: int = Field(..., description="Unique identifier for the job.")
    title: str = Field(..., description="Title of the job.")
    company: str = Field(..., description="Company name.")
    description: str = Field(..., description="Description of the job.")
    required_skills: List[str] = Field(..., description="Required skills for the job.")
    application_deadline: Date = Field(..., description="Deadline for job applications.")
    location: str = Field(..., description="Location of the job.")
    salary: float = Field(..., description="Salary for the job.")
    job_type: str = Field(..., description="Type of the job. Options: FULL, PART, CONT, UNKN")
    active: bool = Field(..., description="Status of the job, whether it is active or not.")

class Match(BaseModel):
    match_id: int = Field(..., description="Unique identifier for the match.")
    uid: str = Field(..., description="User ID associated with the match.")
    job_id: int = Field(..., description="Unique identifier for the job.")
    status: str = Field(..., description="Status of the match.")
    status_code: int = Field(..., description="Status code of the match.")
    grade: float = Field(..., description="Grade assigned to the match.")
    selected_skills: Optional[List[str]] = Field(None, description="List of skills selected by the user for the job.")

class Feedback(BaseModel):
    feedback_id: int = Field(..., description="Unique identifier for the feedback.")
    match_id: int = Field(..., description="Unique identifier for the match.")
    feedback_text: str = Field(..., description="Text of the feedback.")

class User(BaseModel):
    uid: str = Field(..., description="Unique identifier for the user.")
    name: Name = Field(..., description="Name of the user.")
    dob: Date = Field(..., description="Date of birth of the user.")
    is_owner: Optional[bool] = Field(..., description="Whether the user is an owner.")
    is_admin: Optional[bool] = Field(..., description="Whether the user is an admin.")
    phone_number: str = Field(..., description="Phone number of the user. Format: XX-XXXXXXXXXX")
    email: str = Field(..., description="Email of the user.")


if __name__ == "__main__":
    name = Name(first_name="John", last_name="Doe")
    print(name)
    name = str(name)
    print(name)
    name = Name.from_string(name)
    print(name)
    print(type(name))
