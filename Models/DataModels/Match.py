from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from static.CONSTANTS import status_codes
from Errors.GetErrors import Errors as e
import regex as re

class Match(BaseModel):
    match_id: int = Field(..., description="Unique identifier for the match.")
    uid: str = Field(..., description="User ID associated with the match.")
    job_id: int = Field(..., description="Unique identifier for the job.")
    status: str = Field(..., description="Status of the match.")
    status_code: int = Field(..., description="Status code of the match.")
    grade: float = Field(..., description="Grade assigned to the match.")
    selected_skills: Optional[List[str]] = Field(None, description="List of skills selected by the user for the job.")

    @staticmethod
    def generate_default():
        return Match(
            match_id = 0,
            uid = "DEFAULT UID",
            job_id = 0,
            status = status_codes.get_status(status_codes.APPLIED),
            status_code = status_codes.APPLIED,
            grade = 0.0,
            selected_skills = []
        )
    
    @field_validator('match_id')
    def match_id_must_be_valid(cls, v):
        if v < -1:
            raise e.ContentInvalid.MatchIdInvalid(v, "Match ID must be a positive integer")
        return v
    
    @field_validator('uid')
    def uid_must_be_valid(cls, v):
        if len(v) < 10:
            raise e.ContentInvalid.UIDInvalid(v, "UID must be at least 10 characters long")
        if re.match(r'[=;]', v):
            raise e.ContentInvalid.UIDInvalid(v, "UID must contain only letters and numbers.")
        return v
    
    @field_validator('job_id')
    def job_id_must_be_valid(cls, v):
        if v < -1:
            raise e.ContentInvalid.JobIdInvalid(v, "Job ID must be a positive integer")
        return v
    
    @field_validator('status')
    def status_must_be_valid(cls, v):
        if len(v) < 2:
            raise e.ContentInvalid.StatusInvalid(v, "Status must be at least 2 characters long")
        if re.match(r'[=;]', v):
            raise e.ContentInvalid.StatusInvalid(v, "Status must contain only letters, numbers and spaces")
        return v
    
    @field_validator('status_code')
    def status_code_must_be_valid(cls, v):
        if v < 0:
            raise e.ContentInvalid.StatusCodeInvalid(v, "Status code must be a positive integer")
        return v
    
    @field_validator('grade')
    def grade_must_be_valid(cls, v):
        if v < -3.0 or v > 100.0:
            raise e.ContentInvalid.GradeInvalid(v, "Grade must be a float between 0.0 and 10.0")
        return v
    


