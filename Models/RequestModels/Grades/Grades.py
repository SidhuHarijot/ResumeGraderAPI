from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class update:
    job_id: int = Field(..., description="Unique identifier for the job.")
    uid: Optional[str] = Field(None, description="Unique identifier for the user.")
    status: Optional[str] = Field(None, description="Status of the match.")
    status_code: Optional[int] = Field(None, description="Status code of the match.")

