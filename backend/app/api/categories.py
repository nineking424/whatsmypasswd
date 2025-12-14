from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.api.auth import verify_token
from app.models import Category, Credential
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_token),
):
    """List all categories with credential counts."""
    # Subquery for credential count
    count_subquery = (
        select(
            Credential.category_id,
            func.count(Credential.id).label("credential_count"),
        )
        .group_by(Credential.category_id)
        .subquery()
    )

    query = (
        select(
            Category,
            func.coalesce(count_subquery.c.credential_count, 0).label("credential_count"),
        )
        .outerjoin(count_subquery, Category.id == count_subquery.c.category_id)
        .order_by(Category.name)
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        CategoryResponse(
            id=row.Category.id,
            name=row.Category.name,
            color=row.Category.color,
            created_at=row.Category.created_at,
            updated_at=row.Category.updated_at,
            credential_count=row.credential_count,
        )
        for row in rows
    ]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_token),
):
    """Get a single category by ID."""
    # Count credentials
    count_query = (
        select(func.count(Credential.id))
        .where(Credential.category_id == category_id)
    )
    credential_count = await db.scalar(count_query)

    query = select(Category).where(Category.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return CategoryResponse(
        id=category.id,
        name=category.name,
        color=category.color,
        created_at=category.created_at,
        updated_at=category.updated_at,
        credential_count=credential_count,
    )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_token),
):
    """Create a new category."""
    # Check for duplicate name
    query = select(Category).where(Category.name == data.name)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists",
        )

    category = Category(**data.model_dump())
    db.add(category)
    await db.flush()

    return CategoryResponse(
        id=category.id,
        name=category.name,
        color=category.color,
        created_at=category.created_at,
        updated_at=category.updated_at,
        credential_count=0,
    )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_token),
):
    """Update an existing category."""
    query = select(Category).where(Category.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    # Check for duplicate name if updating
    if "name" in update_data and update_data["name"] != category.name:
        name_query = select(Category).where(Category.name == update_data["name"])
        name_result = await db.execute(name_query)
        if name_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists",
            )

    for key, value in update_data.items():
        setattr(category, key, value)

    await db.flush()

    # Count credentials
    count_query = (
        select(func.count(Credential.id))
        .where(Credential.category_id == category_id)
    )
    credential_count = await db.scalar(count_query)

    return CategoryResponse(
        id=category.id,
        name=category.name,
        color=category.color,
        created_at=category.created_at,
        updated_at=category.updated_at,
        credential_count=credential_count,
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_token),
):
    """Delete a category. Credentials in this category will have their category_id set to null."""
    query = select(Category).where(Category.id == category_id)
    result = await db.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    # Set category_id to null for related credentials
    from sqlalchemy import update
    await db.execute(
        update(Credential)
        .where(Credential.category_id == category_id)
        .values(category_id=None)
    )

    await db.delete(category)
