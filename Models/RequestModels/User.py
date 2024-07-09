from pydantic import BaseModel, Field
from typing import Optional
from Models.DataModels.User import User
from Models.DataModels.Name import Name
from Models.DataModels.Date import Date

class Create(BaseModel):
    uid: str = Field(..., description="Unique identifier for the user.")
    first_name: str = Field(..., description="First name of the user.")
    last_name: str = Field(..., description="Last name of the user.")
    dob: str = Field(..., description="Date of birth of the user in DDMMYYYY format.")
    phone_number: str = Field(..., description="Phone number of the user. Format: XX-XXXXXXXXXX")
    email: str = Field(..., description="Email of the user.")

    def to_user(self):
        return User(uid=self.uid, 
                    name=Name(first_name=self.first_name, last_name=self.last_name),
                    dob=Date.create(self.dob),
                    is_owner=False,
                    is_admin=False,
                    phone_number=self.phone_number,
                    email=self.email)


class Update(BaseModel):
    uid: str = Field(None, description="Unique identifier for the user.")
    first_name: Optional[str] = Field(None, description="First name of the user.")
    last_name: Optional[str] = Field(None, description="Last name of the user.")
    dob: Optional[str] = Field(None, description="Date of birth of the user in DDMMYYYY format.")
    phone_number: Optional[str] = Field(None, description="Phone number of the user. Format: XX-XXXXXXXXXX")
    email: Optional[str] = Field(None, description="Email of the user.")

    def to_user(self, current: User):
        if self.first_name:
            current.name.first_name = self.first_name
        if self.last_name:
            current.name.last_name = self.last_name
        if self.dob:
            current.dob = Date.create(self.dob)
        if self.phone_number:
            current.phone_number = self.phone_number
        if self.email:
            current.email = self.email
        return current


class SaveJob(BaseModel):
    uid: str = Field(..., description="Unique identifier for the user.")
    job_id: int = Field(..., description="Unique identifier for the job.")

    def to_user(self, current: User):
        current.saved_jobs.append(self.job_id)
        return current

