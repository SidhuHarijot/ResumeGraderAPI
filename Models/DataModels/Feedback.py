from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from Errors.GetErrors import Errors as e
import regex as re

class Feedback(BaseModel):
    feedback_id: int = Field(..., description="Unique identifier for the feedback.")
    match_id: int = Field(..., description="Unique identifier for the match.")
    feedback_text: str = Field(..., description="Text of the feedback.")
    auth_uid: str = Field(..., description="Unique identifier for the user who created the feedback.")

    @field_validator('feedback_id')
    def feedback_id_must_be_valid(cls, v):
        if v < -1:
            raise e.ContentInvalid.FeedbackIdInvalid(v, "Feedback ID must be a positive integer")
        return v
    
    @field_validator('match_id')
    def match_id_must_be_valid(cls, v):
        if v < 0:
            raise e.ContentInvalid.MatchIdInvalid(v, "Match ID must be a positive integer")
        return v
    
    @field_validator('feedback_text')
    def feedback_text_must_be_valid(cls, v):
        if len(v) < 2:
            raise e.ContentInvalid.FeedbackInvalid(v, "Feedback must be at least 2 characters long")
        if re.match(r'[=;]', v):
            raise e.ContentInvalid.FeedbackInvalid(v, "Feedback must contain only letters, numbers, spaces, and special characters including [, ], and /")
        return v
    
    @field_validator('auth_uid')
    def auth_uid_must_be_valid(cls, v):
        if len(v) < 2:
            raise e.ContentInvalid.FeedbackInvalid(v, "Auth UID must be at least 2 characters long")
        if re.match(r'[=;]', v):
            raise e.ContentInvalid.FeedbackInvalid(v, "Auth UID must contain only letters and numbers.")
        return v
