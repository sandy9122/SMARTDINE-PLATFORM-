from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Restaurants, Branches, Tables
from app.schemas.restaurant import (
    TableCreate,
    TableUpdate,
    TableResponse,
    BranchCreate,
    BranchUpdate,
    BranchResponse,
)
from app.api.auth.auth import get_current_restaurant_owner

router = APIRouter(prefix="/tables", tags=["tables"])


@router.post(
    "/{restaurant_id}",
    response_model=TableResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_table(
    restaurant_id: int,
    table_in: TableCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_restaurant_owner),
):
    """Restaurant owner creates a table for their restaurant."""
    # Verify restaurant exists and user has access
    restaurant = db.query(Restaurants).filter(Restaurants.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    # Generate a secure QR token
    import secrets
    qr_token = secrets.token_urlsafe(16)

    table = Tables(
        restaurant_id=restaurant_id,
        table_number=table_in.table_number,
        capacity=table_in.capacity,
        qr_status="active",
        qr_token=qr_token,
    )
    db.add(table)
    db.commit()
    db.refresh(table)

    return table


@router.get("/{restaurant_id}", response_model=list[TableResponse])
def list_tables(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_restaurant_owner),
):
    """Restaurant owner lists all tables for their restaurant."""
    restaurant = db.query(Restaurants).filter(Restaurants.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    tables = db.query(Tables).filter(Tables.restaurant_id == restaurant_id).all()
    return tables


@router.patch("/{table_id}", response_model=TableResponse)
def update_table(
    table_id: int,
    table_in: TableUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_restaurant_owner),
):
    """Restaurant owner updates a table."""
    table = db.query(Tables).filter(Tables.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found",
        )

    # Tenant isolation check
    restaurant = db.query(Restaurants).filter(Restaurants.id == table.restaurant_id).first()
    if restaurant.owner_id != current_user.id and current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this table",
        )

    for field, value in table_in.dict(exclude_unset=True).items():
        setattr(table, field, value)

    db.commit()
    db.refresh(table)
    return table


@router.post("/{restaurant_id}/branches", response_model=BranchResponse)
def create_branch(
    restaurant_id: int,
    branch_in: BranchCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_restaurant_owner),
):
    """Restaurant owner creates a branch."""
    restaurant = db.query(Restaurants).filter(Restaurants.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    # Check if branch with same name exists
    existing = (
        db.query(Branches)
        .filter(Branches.restaurant_id == restaurant_id, Branches.name == branch_in.name)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Branch with this name already exists",
        )

    branch = Branches(
        restaurant_id=restaurant_id,
        name=branch_in.name,
        address=branch_in.address,
        contact_phone=branch_in.contact_phone,
        operating_hours=branch_in.operating_hours,
        is_primary=branch_in.is_primary,
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)

    return branch