from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Create(BaseModel):
    match_id: int = Field(..., description="Unique identifier for the match.")
    feedback_text: str = Field(..., description="Text of the feedback.")


class Update(BaseModel):
    feedback_id: int = Field(..., description="Unique identifier for the feedback.")
    feedback_text: str = Field(..., description="Text of the feedback.")


class Get(BaseModel):
    feedback_id: Optional[int] = Field(None, description="Unique identifier for the feedback.")
    match_id: Optional[int] = Field(None, description="Unique identifier for the match.")
    feedback_text: Optional[str] = Field(None, description="Text of the feedback.")
    all_feedback: Optional[bool] = Field(True, description="Flag to get all feedbacks.")
