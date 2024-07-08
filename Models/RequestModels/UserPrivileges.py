from pydantic import BaseModel, Field
from typing import Optional
from Models.DataModels.User import User

class Update(BaseModel):
    target_uid: str = Field(..., description="UID of the user whose privileges are being updated.")
    is_admin: Optional[bool] = Field(None, description="Whether the user should be an admin.")
    is_owner: Optional[bool] = Field(None, description="Whether the user should be an owner.")
    auth_uid: str = Field(..., description="UID of the admin or owner authorizing the action.")

    def to_user(self, current: User):
        if self.is_admin is not None:
            current.is_admin = self.is_admin
        if self.is_owner is not None:
            current.is_owner = self.is_owner
        return current