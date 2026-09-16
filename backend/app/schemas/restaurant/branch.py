from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ===== Branch Schemas =====

class BranchCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Branch name")
    address: Optional[str] = Field(None, description="Branch address")
    contact_phone: Optional[str] = Field(
        None, max_length=50, description="Branch contact phone"
    )
    operating_hours: Optional[str] = Field(
        None, max_length=100, description="Operating hours"
    )
    is_primary: Optional[bool] = Field(
        default=False, description="Whether this is the primary branch"
    )


class BranchUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None)
    contact_phone: Optional[str] = Field(None, max_length=50)
    operating_hours: Optional[str] = Field(None, max_length=100)
    is_primary: Optional[bool] = Field(None)


class BranchResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    address: Optional[str]
    contact_phone: Optional[str]
    operating_hours: Optional[str]
    status: str
    is_primary: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True