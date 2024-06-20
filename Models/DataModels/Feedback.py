from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class Feedback(BaseModel):
    feedback_id: int = Field(..., description="Unique identifier for the feedback.")
    match_id: int = Field(..., description="Unique identifier for the match.")
    feedback_text: str = Field(..., description="Text of the feedback.")

