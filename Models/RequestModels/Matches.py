from pydantic import BaseModel, Field, field_validator
from typing import Optional

class Create(BaseModel):
    uid: str = Field(..., description="Unique identifier for the user.")
    job_id: int = Field(..., description="Unique identifier for the job.")


class Get(BaseModel):
    uid: Optional[str] = Field(None, description="Unique identifier for the user.")
    job_id: Optional[int] = Field(None, description="Unique identifier for the job.")
    status: Optional[str] = Field(None, description="Status of the match.")
    status_code: Optional[int] = Field(None, description="Status code of the match.")

class Update(BaseModel):
    match_id: Optional[int] = Field(None, description="Unique identifier for the match.")
    job_id: Optional[int] = Field(None, description="Unique identifier for the job.")
    uid: Optional[str] = Field(None, description="Unique identifier for the user.")
    status: Optional[str] = Field(None, description="Status of the match.")
    status_code: Optional[int] = Field(None, description="Status code of the match.")

