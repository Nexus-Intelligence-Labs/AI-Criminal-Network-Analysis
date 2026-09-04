from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    username: str = Field(..., description="The username of the user.")
    password: str = Field(..., description="The plain text password of the user.")

class LoginResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the authentication was successful.")
    message: str = Field(..., description="A safe message about the authentication status.")
    user_id: Optional[int] = Field(None, description="The ID of the authenticated user if successful.")


