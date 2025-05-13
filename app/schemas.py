from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class RefreshRequest(BaseModel):
    refresh_token: str
    user_guid: str

class UserResponse(BaseModel):
    user_guid: str
    user_ip: Optional[str] = None 
    access_token_id: Optional[str] = None 

    class Config:
        orm_mode = True 