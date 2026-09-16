from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ===== Auth Schemas =====

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    role: str = Field(
        default="customer",
        description="User role: super_admin, restaurant_owner, restaurant_admin, manager, kitchen, waiter, cashier, customer",
    )
    restaurant_id: Optional[int] = Field(
        default=None, description="Associated restaurant ID (for restaurant roles)"
    )


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    restaurant_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=30 * 60, description="Token expires in seconds")


# ===== Password Reset Schemas =====

class PasswordReset(BaseModel):
    user_id: int = Field(..., description="User ID")
    new_password: str = Field(
        ..., min_length=6, description="New password to set"
    )


# ===== Customer Guest Schemas =====

class GuestSession(BaseModel):
    guest_token: str = Field(..., description="Unique guest session token")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    restaurant_id: int = Field(..., description="Associated restaurant ID")


# ===== Profile Update Schemas =====

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    preferences: Optional[dict] = Field(None, description="Customer preferences JSON")


# ===== Role-based access schemas =====

class RoleCheck(BaseModel):
    required_role: str = Field(
        description="Required role: super_admin, restaurant_owner, restaurant_admin, manager, kitchen, waiter, cashier, customer"
    )
    allowed_roles: list = Field(
        default=["super_admin", "restaurant_owner", "restaurant_admin"],
        description "List of roles allowed to access the endpoint",
    )


# ===== Table QR Schemas =====

class QrToken(BaseModel):
    token: str = Field(..., description="QR token for table resolution")
    restaurant_id: int = Field(..., description="Resolved restaurant ID")
    branch_id: Optional[int] = Field(None, description="Resolved branch ID")
    table_id: int = Field(..., description="Resolved table ID")


# ===== Menu Item Schemas =====

class MenuItemSearch(BaseModel):
    query: Optional[str] = Field(None, description="Search query for item name")
    category_id: Optional[int] = Field(None, description="Filter by category")
    is_veg: Optional[bool] = Field(None, description="Filter vegetarian only")
    is_active: Optional[bool] = Field(None, description="Filter active items only")
    min_price: Optional[int] = Field(None, ge=0, description="Minimum price in cents")
    max_price: Optional[int] = Field(None, ge=0, description="Maximum price in cents")
    spicy_level: Optional[str] = Field(None, description="Filter by spice level")


# ===== Order Schemas =====

class OrderItemCreate(BaseModel):
    menu_item_id: int = Field(..., description="Menu item ID")
    variant_id: Optional[int] = Field(None, description="Variant ID if applicable")
    quantity: int = Field(default=1, ge=1, description="Item quantity")
    addon_ids: Optional[list] = Field(
        default=None, description="List of addon IDs to include"
    )
    special_instructions: Optional[str] = Field(
        default=None, max_length=500, description="Special customization instructions"
    )


class OrderCreate(BaseModel):
    restaurant_id: int = Field(..., description="Restaurant ID")
    branch_id: Optional[int] = Field(None, description="Branch ID")
    table_id: int = Field(..., description="Table ID")
    guest_token: Optional[str] = Field(None, description="Guest token if not logged in")
    items: list = Field(..., description="List of order items")
    special_instructions: Optional[str] = Field(
        default=None, max_length=500, description="Order special instructions"
    )


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    variant_name: Optional[str] = Field(None, description="Variant name")
    quantity: int
    price: int  # in cents
    discount_amount: int = Field(default=0, description="Discount in cents")
    addons: list = Field(default=[], description="Selected addons")
    special_instructions: Optional[str]

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    status: str
    total_amount: int  # in cents
    discount_amount: int = Field(default=0, description="Discount in cents")
    tax_amount: int = Field(default=0, description="Tax in cents")
    final_amount: int  # in cents
    created_at: datetime
    table: Optional[dict] = Field(None, description="Table information")
    items: list = Field(default=[], description="Order items")

    class Config:
        from_attributes = True