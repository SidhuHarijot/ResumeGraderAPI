from pydantic import BaseModel, Field, field_validator
from typing import List
from .Experience import Experience
from .Education import Education
from Errors.GetErrors import Errors as e
import regex as re

class Resume(BaseModel):
    uid: str = Field(..., description="User ID associated with the resume.")
    skills: List[str] = Field(..., description="List of skills.")
    experience: List[Experience] = Field(..., description="List of experiences.")
    education: List[Education] = Field(..., description="List of education records.")

    @field_validator('uid')
    def uid_must_be_valid(cls, v):
        if len(v) < 1 or len(v) > 50:
            raise e.ContentInvalid.UIDInvalid(v, "UID must be between 2 and 50 characters")
        if re.match(r'[=;]', v):
            raise e.ContentInvalid.UIDInvalid(v, "UID contains invalid characters")
        return v
    
    @field_validator('skills')
    def skills_must_be_valid(cls, v):
        for skill in v:
            if len(skill) < 2:
                raise e.ContentInvalid.SkillsInvalid(v, "Skills must be at least 2 characters long")
            if re.match(r'[=;]', skill):
                raise e.ContentInvalid.SkillsInvalid(v, "Skills contain invalid characters")
        return v

    def __str__(self) -> str:
        return f"User: {self.uid}. Skills: {', '.join(self.skills)}. Experiences: {', '.join([str(exp) for exp in self.experience])}. Education: {', '.join([str(edu) for edu in self.education])}."

