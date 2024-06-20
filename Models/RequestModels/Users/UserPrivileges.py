from pydantic import BaseModel, Field
from typing import List, Optional

class UpdateUserPrivilegesRequest(BaseModel):
    target_uid: str = Field(..., description="UID of the user whose privileges are being updated.")
    is_admin: Optional[bool] = Field(None, description="Whether the user should be an admin.")
    is_owner: Optional[bool] = Field(None, description="Whether the user should be an owner.")
    auth_uid: str = Field(..., description="UID of the admin or owner authorizing the action.")
