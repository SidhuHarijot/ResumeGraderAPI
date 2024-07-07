from pydantic import BaseModel, Field, field_validator
from typing import Optional
from Models.DataModels.Feedback import Feedback as fb
from Models.DataModels.Date import Date


class Create(BaseModel):
    match_id: int = Field(..., description="Unique identifier for the match.")
    feedback_text: str = Field(..., description="Text of the feedback.")
    auth_uid: str = Field(..., description="Unique identifier for the user who created the feedback.")

    def to_feedback(self):
        self.feedback_text = Date.today().display() + " " + self.feedback_text
        return fb(
            feedback_id=-1,
            match_id=self.match_id,
            feedback_text=self.feedback_text,
            auth_uid=self.auth_uid
        )


class Update(BaseModel):
    feedback_id: Optional[int] = Field(..., description="Unique identifier for the feedback.")
    match_id: Optional[int] = Field(None, description="Unique identifier for the match.")
    feedback_text: str = Field(..., description="Text of the feedback.")
    auth_uid: str = Field(..., description="Unique identifier for the user who created the feedback.")

    def to_feedback(self, current: fb):
        if self.feedback_id or self.match_id:
            self.feedback_text = Date.today().display() + " " + self.feedback_text + " \n\n\n " + current.feedback_text
            return fb(
                feedback_id=self.feedback_id,
                match_id=self.match_id,
                feedback_text=self.feedback_text,
                auth_uid=self.auth_uid
            )
        raise ValueError("feedback_id or match_id must be provided.")


class Get(BaseModel):
    feedback_id: Optional[int] = Field(None, description="Unique identifier for the feedback.")
    match_id: Optional[int] = Field(None, description="Unique identifier for the match.")
    feedback_text: Optional[str] = Field(None, description="Text of the feedback.")
    all_feedback: Optional[bool] = Field(True, description="Flag to get all feedbacks.")
