"""Browse the catalogue: list, search and paginate products."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Product
from app.schemas import ProductOut, ProductPage

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductPage)
def list_products(
    q: str | None = Query(default=None, max_length=100, description="Search name and description"),
    page: int = Query(default=0, ge=0, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    query = select(Product)
    if q:
        pattern = f"%{q}%"
        query = query.where(or_(Product.name.ilike(pattern), Product.description.ilike(pattern)))

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    offset = page * page_size
    products = db.scalars(query.order_by(Product.id).offset(offset).limit(page_size)).all()
    return ProductPage(
        items=[ProductOut.model_validate(p) for p in products],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
