from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from Models.DataModels.Experience import Experience
from Models.DataModels.Education import Education
from Models.DataModels.Resume import Resume
from fastapi import UploadFile


class Create(BaseModel):
    uid: str = Field(..., description="Unique identifier for the user.")
    skills: Optional[List[str]] = Field(default=[], description="List of skills selected by the user for the job.")
    education: Optional[List[Education]] = Field(default=[], description="Education level of the user.")
    experience: Optional[List[Experience]] = Field(default=[], description="Experience of the user.")

    def to_resume(self):
        return Resume(
            uid=self.uid,
            skills=self.skills,
            education=self.education,
            experience=self.experience
        )


class Update(BaseModel):
    uid: str = Field(..., description="Unique identifier for the user.")
    skills: Optional[List[str]] = Field(None, description="List of skills selected by the user for the job.")
    education: Optional[List[Education]] = Field(None, description="Education level of the user.")
    experience: Optional[List[Experience]] = Field(None, description="Experience of the user.")

    def to_resume(self, current:Resume):
        if self.skills:
            current.skills = self.skills
        if self.education:
            current.education = self.education
        if self.experience:
            current.experience = self.experience
        return current
