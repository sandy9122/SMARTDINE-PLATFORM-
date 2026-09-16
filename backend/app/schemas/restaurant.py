from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


# ===== Restaurant Schemas =====

class RestaurantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Restaurant name")
    description: Optional[str] = Field(None, max_length=500, description="Restaurant description")
    cuisine_type: Optional[str] = Field(None, max_length=100, description="Cuisine type")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    email: Optional[EmailStr] = Field(None, max_length=255, description="Restaurant email")
    address: Optional[str] = Field(None, description="Street address")
    opening_time: Optional[str] = Field(None, max_length=10, description="Opening time (HH:MM)")
    closing_time: Optional[str] = Field(None, max_length=10, description="Closing time (HH:MM)")
    gst_number: Optional[str] = Field(None, max_length=50, description="GST number")
    website: Optional[str] = Field(None, max_length=500, description="Website URL")
    social_media: Optional[str] = Field(None, description="Social media links JSON")


class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Restaurant name")
    description: Optional[str] = Field(
        None, max_length=500, description="Restaurant description"
    )
    cuisine_type: Optional[str] = Field(
        None, max_length=100, description="Cuisine type"
    )
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    email: Optional[EmailStr] = Field(
        None, max_length=255, description="Restaurant email"
    )
    address: Optional[str] = Field(None, description="Street address")
    opening_time: Optional[str] = Field(
        None, max_length=10, description="Opening time (HH:MM)"
    )
    closing_time: Optional[str] = Field(
        None, max_length=10, description="Closing time (HH:MM)"
    )
    gst_number: Optional[str] = Field(None, max_length=50, description="GST number")
    website: Optional[str] = Field(None, max_length=500, description="Website URL")
    social_media: Optional[str] = Field(None, description="Social media links JSON")
    status: Optional[str] = Field(None, description="Restaurant status (active/closed)")


class RestaurantResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    phone: Optional[str]
    email: Optional[EmailStr]
    address: Optional[str]
    cuisine_type: Optional[str]
    opening_time: Optional[str]
    closing_time: Optional[str]
    status: str
    gst_number: Optional[str]
    website: Optional[str]
    social_media: Optional[str]
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


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


# ===== Table Schemas =====

class TableCreate(BaseModel):
    table_number: str = Field(..., min_length=1, max_length=20, description="Table number")
    capacity: Optional[int] = Field(
        default=4, ge=1, le=50, description="Table capacity"
    )
    qr_status: Optional[str] = Field(
        default="active",
        description="QR code status",
    )


class TableUpdate(BaseModel):
    table_number: Optional[str] = Field(None, min_length=1, max_length=20)
    capacity: Optional[int] = Field(None, ge=1, le=50)
    qr_status: Optional[str] = Field(None)


class TableResponse(BaseModel):
    id: int
    restaurant_id: int
    branch_id: Optional[int]
    table_number: str
    capacity: int
    status: str
    qr_status: str
    qr_token: Optional[str] = None

    class Config:
        from_attributes = True


# ===== Category Schemas =====

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Category name")
    parent_id: Optional[int] = Field(
        default=None, description="Parent category ID for subcategories"
    )
    display_order: Optional[int] = Field(
        default=0, ge=0, le=1000, description="Display order"
    )
    is_active: Optional[bool] = Field(default=True)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    parent_id: Optional[int] = Field(None)
    display_order: Optional[int] = Field(None, ge=0, le=1000)
    is_active: Optional[bool] = Field(None)


class CategoryResponse(BaseModel):
    id: int
    restaurant_id: int
    parent_id: Optional[int]
    name: str
    display_order: int
    is_active: bool
    children: List["CategoryResponse"] = Field(default=[], alias="children")

    class Config:
        from_attributes = True


# ===== Menu Item Schemas =====

class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Menu item name")
    description: Optional[str] = Field(
        None, max_length=500, description="Menu item description"
    )
    category_id: Optional[int] = Field(
        default=None, description="Category ID"
    )
    price: int = Field(
        ge=0, description="Price in cents"
    )
    discount_price: Optional[int] = Field(
        ge=0, default=None, description="Discount price in cents (nullable)"
    )
    tax_percentage: Optional[int] = Field(
        ge=0, le=100, default=0, description="Tax percentage"
    )
    is_veg: Optional[bool] = Field(default=True, description="Is vegetarian")
    preparation_time: Optional[int] = Field(
        ge=1, le=180, default=15, description="Preparation time in minutes"
    )
    is_active: Optional[bool] = Field(default=True)
    is_bestseller: Optional[bool] = Field(default=False)
    is_today_special: Optional[bool] = Field(default=False)
    spicy_level: Optional[str] = Field(
        default="mild", max_length=20, description="Spice level"
    )
    calories: Optional[int] = Field(
        ge=0, default=None, description="Calories"
    )
    display_order: Optional[int] = Field(
        ge=0, le=1000, default=0, description="Display order"
    )
    image_url: Optional[str] = Field(None, max_length=500, description="Menu item image")


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = Field(None)
    price: Optional[int] = Field(None, ge=0)
    discount_price: Optional[int] = Field(None, ge=0)
    tax_percentage: Optional[int] = Field(
        ge=0, le=100, default=None
    )
    is_veg: Optional[bool] = Field(None)
    preparation_time: Optional[int] = Field(
        ge=1, le=180, default=None
    )
    is_active: Optional[bool] = Field(None)
    is_bestseller: Optional[bool] = Field(None)
    is_today_special: Optional[bool] = Field(None)
    spicy_level: Optional[str] = Field(None, max_length=20)
    calories: Optional[int] = Field(None, ge=0)
    display_order: Optional[int] = Field(None, ge=0, le=1000)
    image_url: Optional[str] = Field(None, max_length=500)


class MenuItemResponse(BaseModel):
    id: int
    restaurant_id: int
    category_id: Optional[int]
    name: str
    description: Optional[str]
    price: int
    discount_price: Optional[int]
    tax_percentage: int
    is_veg: bool
    preparation_time: int
    is_active: bool
    is_bestseller: bool
    is_today_special: bool
    spicy_level: str
    calories: Optional[int]
    display_order: int
    image_url: Optional[str]
    category: Optional["CategoryResponse"] = None
    variants: List["MenuItemVariantResponse"] = Field(default=[], alias="variants")
    item_addons: List["MenuItemAddonResponse"] = Field(
        default=[], alias="item_addons"
    )

    class Config:
        from_attributes = True


class MenuItemVariantResponse(BaseModel):
    id: int
    menu_item_id: int
    name: str
    price: int
    is_active: bool

    class Config:
        from_attributes = True


class MenuItemAddonResponse(BaseModel):
    id: int
    menu_item_id: int
    addon_id: int
    addon_name: str
    addon_price: int
    is_required: bool

    class Config:
        from_attributes = True