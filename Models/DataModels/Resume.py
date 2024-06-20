from pydantic import BaseModel, Field, field_validator
from typing import List
from Experience import Experience
from Education import Education

class Resume(BaseModel):
    uid: str = Field(..., description="User ID associated with the resume.")
    skills: List[str] = Field(..., description="List of skills.")
    experience: List[Experience] = Field(..., description="List of experiences.")
    education: List[Education] = Field(..., description="List of education records.")

    def __str__(self) -> str:
        return f"User: {self.uid}. Skills: {', '.join(self.skills)}. Experiences: {', '.join([str(exp) for exp in self.experience])}. Education: {', '.join([str(edu) for edu in self.education])}."

