from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from Models.DataModels.Experience import Experience
from Models.DataModels.Education import Education
from fastapi import UploadFile


class Create(BaseModel):
    uid: Optional[str] = Field(None, description="Unique identifier for the user.")
    skills: Optional[List[str]] = Field(None, description="List of skills selected by the user for the job.")
    education: Optional[Education] = Field(None, description="Education level of the user.")
    experience: Optional[Experience] = Field(None, description="Experience of the user.")
    file: Optional[UploadFile] = Field(None, description="Resume file of the user.")
    resume_text: Optional[str] = Field(None, description="Resume text of the user.")
