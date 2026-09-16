from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint,
    Index,
    Table,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db import Base


# ---------- Core Tables ----------

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), nullable=False, default="customer")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    restaurant = relationship("Restaurants", back_populates="users")
    branches = relationship("Branches", back_populates="owner")
    managed_restaurant = relationship(
        "Restaurants", back_populates="admin", foreign_keys=[restaurant_id]
    )


class Restaurants(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    cover_image_url = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    cuisine_type = Column(String(100), nullable=True)
    opening_time = Column(String(10), nullable=True)
    closing_time = Column(String(10), nullable=True)
    status = Column(String(50), nullable=False, default="active")
    gst_number = Column(String(50), nullable=True)
    website = Column(String(500), nullable=True)
    social_media = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    users = relationship("Users", back_populates="restaurant", foreign_keys=[restaurant_id])
    admin = relationship("Users", back_populates="managed_restaurant", foreign_keys=[owner_id])
    branches = relationship("Branches", back_populates="restaurant", cascade="all, delete-orphan")
    tables = relationship("Tables", back_populates="restaurant", cascade="all, delete-orphan")
    categories = relationship("Categories", back_populates="restaurant", cascade="all, delete-orphan")
    menu_items = relationship("MenuItems", back_populates="restaurant", cascade="all, delete-orphan")
    offers = relationship("Offers", back_populates="restaurant", cascade="all, delete-orphan")
    subscriptions = relationship("Subscriptions", back_populates="restaurant", cascade="all, delete-orphan")


class Branches(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    contact_phone = Column(String(50), nullable=True)
    operating_hours = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="active")
    is_primary = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    restaurant = relationship("Restaurants", back_populates="branches")
    tables = relationship("Tables", back_populates="branch", cascade="all, delete-orphan")


class Tables(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    table_number = Column(String(20), nullable=False)
    capacity = Column(Integer, nullable=True, default=4)
    status = Column(
        String(50),
        nullable=False,
        default="AVAILABLE",
    )
    qr_status = Column(
        String(50),
        nullable=False,
        default="active",
    )
    qr_token = Column(String(100), unique=True, nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Constraints & Indexes
    __table_args__ = (
        UniqueConstraint("restaurant_id", "table_number", name="uq_restaurant_table_number"),
        Index("ix_tables_restaurant_id", "restaurant_id"),
        Index("ix_tables_branch_id", "branch_id"),
        Index("ix_tables_status", "status"),
        Index("ix_tables_qr_token", "qr_token"),
    )

    # Possible states: AVAILABLE, OCCUPIED, ORDERING, WAITING_FOR_SERVICE, BILL_REQUESTED, CLEANING, INACTIVE
    STATE_AVAILABLE = "AVAILABLE"
    STATE_OCCUPIED = "OCCUPIED"
    STATE_ORDERING = "ORDERING"
    STATE_WAITING_FOR_SERVICE = "WAITING_FOR_SERVICE"
    STATE_BILL_REQUESTED = "BILL_REQUESTED"
    STATE_CLEANING = "CLEANING"
    STATE_INACTIVE = "INACTIVE"


# ---------- Menu Model ----------

class Categories(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    name = Column(String(255), nullable=False)
    display_order = Column(Integer, nullable=True, default=0)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    restaurant = relationship("Restaurants", back_populates="categories")
    parent = relationship("Categories", remote_side=[id], backref="children")
    menu_items = relationship("MenuItems", back_populates="category", cascade="all, delete-orphan")


class MenuItems(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False, default=0)  # stored in cents
    discount_price = Column(Integer, nullable=True, default=None)  # stored in cents, nullable
    tax_percentage = Column(Integer, nullable=False, default=0)  # percentage
    is_veg = Column(Boolean, nullable=False, default=True)
    preparation_time = Column(Integer, nullable=True, default=15)  # minutes
    is_active = Column(Boolean, default=True)
    is_bestseller = Column(Boolean, default=False)
    is_today_special = Column(Boolean, default=False, nullable=True)
    spicy_level = Column(String(20), nullable=True, default="mild")
    calories = Column(Integer, nullable=True, default=None)
    display_order = Column(Integer, nullable=True, default=0)
    image_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    restaurant = relationship("Restaurants", back_populates="menu_items")
    category = relationship("Categories", back_populates="menu_items")
    variants = relationship("MenuItemVariants", back_populates="menu_item", cascade="all, delete-orphan")
    order_items = relationship("OrderItems", back_populates="menu_item", cascade="all, delete-orphan")


class MenuItemVariants(Base):
    __tablename__ = "menu_item_variants"

    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False, default=0)  # stored in cents
    is_active = Column(Boolean, default=True)
    sku = Column(String(100), nullable=True, unique=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    menu_item = relationship("MenuItems", back_populates="variants")


# ---------- Add-ons Model ----------

addons_association = Table(
    "menu_item_addons",
    Base.metadata,
    Column("menu_item_id", Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), primary_key=True),
    Column("addon_id", Integer, ForeignKey("addons.id", ondelete="CASCADE"), primary_key=True),
    Column("is_required", Boolean, default=False),
    Column("display_order", Integer, default=0),
)

class Addons(Base):
    __tablename__ = "addons"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False, default=0)  # stored in cents
    is_active = Column(Boolean, default=True)
    category = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    menu_item_addons = relationship("MenuItemAddons", back_populates="addon", cascade="all, delete-orphan")


class MenuItemAddons(Base):
    __tablename__ = "menu_item_addons"

    # Composite key handled via association table, but we keep for explicit relations if needed
    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False)
    addon_id = Column(Integer, ForeignKey("addons.id", ondelete="CASCADE"), nullable=False)
    is_required = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)

    # Relationships
    menu_item = relationship("MenuItems", back_populates="item_addons")
    addon = relationship("Addons", back_populates="menu_item_addons")


# ---------- Offers & Coupons Model ----------

class Offers(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    discount_type = Column(String(20), nullable=False)  # "percentage", "flat", "buy_one_get_one"
    discount_value = Column(Integer, nullable=False)  # stored in cents
    min_order_value = Column(Integer, nullable=True, default=0)  # stored in cents
    max_discount = Column(Integer, nullable=True, default=None)  # stored in cents, max discount amount
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    start_time = Column(String(10), nullable=True)  # e.g., "18:00"
    end_time = Column(String(10), nullable=True)  # e.g., "22:00"
    usage_limit = Column(Integer, nullable=True)  # per customer or overall
    times_used = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    applies_to = Column(String(50), nullable=True)  # "all", "category", "item"

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    restaurant = relationship("Restaurants", back_populates="offers")


class Coupons(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_type = Column(String(20), nullable=False)  # "percentage", "flat"
    discount_value = Column(Integer, nullable=False)  # stored in cents
    min_order_value = Column(Integer, nullable=True, default=0)  # stored in cents
    usage_limit = Column(Integer, nullable=True)  # per customer overall
    times_used = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Constraints
    __table_args__ = (
        UniqueConstraint("restaurant_id", "code", name="uq_restaurant_coupon_code"),
    )


# ---------- Customers Model ----------

class Customers(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    name = Column(String(255), nullable=True)
    guest_token = Column(String(100), unique=True, nullable=True, index=True)
    preferences = Column(Text, nullable=True)  # JSON string for customer preferences
    total_orders = Column(Integer, nullable=False, default=0)
    total_spent = Column(Integer, nullable=False, default=0)  # stored in cents
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# ---------- Orders Model ----------

class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    table_id = Column(Integer, ForeignKey("tables.id", ondelete="SET NULL"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    guest_token = Column(String(100), nullable=True)
    status = Column(
        String(50),
        nullable=False,
        default="PLACED",
    )
    payment_status = Column(
        String(50),
        nullable=False,
        default="pending",
    )
    total_amount = Column(Integer, nullable=False, default=0)  # stored in cents
    tax_amount = Column(Integer, nullable=False, default=0)  # stored in cents
    discount_amount = Column(Integer, nullable=False, default=0)  # stored in cents
    tip_amount = Column(Integer, nullable=False, default=0)  # stored in cents
    final_amount = Column(Integer, nullable=False, default=0)  # stored in cents
    notes = Column(Text, nullable=True)
    preparation_time_estimate = Column(Integer, nullable=True, default=0)  # minutes
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    restaurant = relationship("Restaurants", back_populates="orders")
    branch = relationship("Branches", back_populates="orders")
    table = relationship("Tables", back_populates="orders")
    customer = relationship("Customers", back_populates="orders")
    status_history = relationship(
        "OrderStatusHistory", back_populates="order", cascade="all, delete-orphan"
    )
    order_items = relationship(
        "OrderItems", back_populates="order", cascade="all, delete-orphan"
    )
    payment = relationship("Payments", back_populates="order", uselist=False, cascade="all, delete-orphan")


# ---------- Order Status History Model ----------

class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    previous_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    changed_by = Column(String(100), nullable=True)  # "system", "waiter", "kitchen", "customer"
    changed_by_id = Column(Integer, nullable=True)  # user ID or null for system
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    order = relationship("Orders", back_populates="status_history")

    # Indexes for analytics
    __table_args__ = (
        Index("ix_order_status_history_order_id", "order_id"),
        Index("ix_order_status_history_created_at", "created_at"),
    )


# ---------- Payments Model ----------

class Payments(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(100), nullable=False)  # e.g., "stripe", "razorpay", "paypal"
    provider_payment_id = Column(String(255), nullable=True)  # payment provider's ID
    amount = Column(Integer, nullable=False)  # stored in cents
    currency = Column(String(3), nullable=False, default="INR")  # USD, INR, etc.
    status = Column(
        String(50),
        nullable=False,
        default="pending",
    )  # pending, processing, success, failed, refunded
    transaction_reference = Column(String(255), nullable=True)
    card_last_four = Column(String(4), nullable=True)  # last 4 digits of card (masked)
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    captured = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    order = relationship("Orders", back_populates="payment")


# ---------- Plans & Subscriptions Model ----------

class Plans(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # STARTER, BUSINESS, ENTERPRISE
    price = Column(Integer, nullable=False)  # monthly price in cents
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Limits
    max_branches = Column(Integer, nullable=True)  # None = unlimited
    max_tables = Column(Integer, nullable=True)  # None = unlimited
    max_staff = Column(Integer, nullable=True)  # None = unlimited
    max_orders_per_month = Column(Integer, nullable=True)  # None = unlimited
    features = Column(Text, nullable=True)  # JSON string of included features

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Constraints
    __table_args__ = (
        UniqueConstraint("name", name="uq_plan_name"),
    )


class Subscriptions(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    status = Column(String(50), nullable=False, default="active")  # active, cancelled, past_due, trialing
    stripe_subscription_id = Column(String(255), nullable=True)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, nullable=False, default=False)
    quantity = Column(Integer, nullable=False, default=1)  # number of licenses/seats
    amount = Column(Integer, nullable=False)  # billed amount in cents
    currency = Column(String(3), nullable=False, default="INR")
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    restaurant = relationship("Restaurants", back_populates="subscriptions")
    plan = relationship("Plans", back_populates="subscriptions")