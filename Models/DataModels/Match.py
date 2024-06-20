from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class Match(BaseModel):
    match_id: int = Field(..., description="Unique identifier for the match.")
    uid: str = Field(..., description="User ID associated with the match.")
    job_id: int = Field(..., description="Unique identifier for the job.")
    status: str = Field(..., description="Status of the match.")
    status_code: int = Field(..., description="Status code of the match.")
    grade: float = Field(..., description="Grade assigned to the match.")
    selected_skills: Optional[List[str]] = Field(None, description="List of skills selected by the user for the job.")

