from pydantic import BaseModel, Field, field_validator
from typing import Optional
from Models.DataModels.Match import Match
from fastapi import Query
from static.CONSTANTS import status_codes

class Create(BaseModel):
    uid: str = Field(..., description="Unique identifier for the user.")
    job_id: int = Field(..., description="Unique identifier for the job.")
    selected_skills: Optional[list] = Field(None, description="List of skills selected by the user for the job.")

    def to_match(self):
        match_data = Match.generate_default()
        match_data.uid = self.uid
        match_data.job_id = self.job_id
        match_data.selected_skills = self.selected_skills
        return match_data


class Get(BaseModel):
    match_id : Optional[int] = Query(None, description="Unique identifier for the match.")
    uid: Optional[str] = Query(None, description="Unique identifier for the user.")
    job_id: Optional[int] = Query(None, description="Unique identifier for the job.")
    status: Optional[str] = Query(None, description="Status of the match.")
    status_code: Optional[int] = Query(None, description="Status code of the match.")
    grade_greater_than: Optional[float] = Query(None, description="Grade assigned to the match.")

    def get_find_params(self):
        return_data = {}
        if self.match_id is not None:
            return_data[("match_id", "=")] = self.match_id
        if self.uid is not None:
            return_data[("uid", "=")] = self.uid
        if self.job_id is not None:
            return_data[("job_id", "=")] = self.job_id
        if self.status is not None:
            return_data[("status", "=")] = self.status
        if self.status_code is not None:
            return_data[("status_code", "=")] = self.status_code
        if self.grade_greater_than is not None:
            return_data[("grade", ">")] = self.grade_greater_than
        return return_data

    def get_dict(self):
        return {k: v for k, v in self.model_dump().items() if v is not None}

    def __str__(self):
        return str(self.get_dict())
                

class Update(BaseModel):
    match_id: int = Field(..., description="Unique identifier for the match.")
    status: Optional[str] = Field(None, description="Status of the match.")
    status_code: Optional[int] = Field(None, description="Status code of the match.")
    auth_uid: str = Field(..., description="Unique identifier for the user.")

    def to_match(self, current: Match, add_auth: str = None):
        match_data = current
        if self.status is not None:
            match_data.status = self.status + " By " + add_auth if add_auth else self.status
        if self.status_code is not None:
            match_data.status_code = self.status_code
            if self.status is None:
                match_data.status = status_codes.get_status(self.status_code) + " BY " + add_auth if add_auth else status_codes.get_status(self.status_code)
        return match_data

