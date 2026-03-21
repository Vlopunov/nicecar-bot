from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.api.deps import get_admin_user
from app.models import ServiceCategory, Service, ServicePrice, User
from decimal import Decimal

router = APIRouter(prefix="/api/admin", tags=["admin-services"])


class CategoryData(BaseModel):
    name: str
    icon: str = "🔧"
    description: str | None = None
    sort_order: int = 0
    is_active: bool = True


class ServiceData(BaseModel):
    category_id: int
    name: str
    description: str | None = None
    duration_min_hours: float = 1.0
    duration_max_hours: float = 2.0
    has_car_classes: bool = False
    is_package: bool = False
    sort_order: int = 0
    is_active: bool = True


class PriceData(BaseModel):
    service_id: int
    car_class: str | None = None
    package_name: str | None = None
    price_from: float
    price_to: float | None = None
    description: str | None = None


# Categories CRUD
@router.get("/categories")
async def list_categories(_: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ServiceCategory).order_by(ServiceCategory.sort_order))
    cats = result.scalars().all()
    return [{"id": c.id, "name": c.name, "icon": c.icon, "description": c.description,
             "sort_order": c.sort_order, "is_active": c.is_active} for c in cats]


@router.post("/categories")
async def create_category(data: CategoryData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    cat = ServiceCategory(**data.model_dump())
    session.add(cat)
    await session.commit()
    await session.refresh(cat)
    return {"id": cat.id, "name": cat.name}


@router.put("/categories/{cat_id}")
async def update_category(cat_id: int, data: CategoryData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    cat = await session.get(ServiceCategory, cat_id)
    if not cat:
        return {"error": "Not found"}
    for k, v in data.model_dump().items():
        setattr(cat, k, v)
    await session.commit()
    return {"id": cat.id, "name": cat.name}


# Services CRUD
@router.get("/services")
async def list_services_admin(_: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Service).options(selectinload(Service.prices)).order_by(Service.category_id, Service.sort_order)
    )
    services = result.scalars().unique().all()
    return [
        {
            "id": s.id, "category_id": s.category_id, "name": s.name, "description": s.description,
            "duration_min_hours": float(s.duration_min_hours), "duration_max_hours": float(s.duration_max_hours),
            "has_car_classes": s.has_car_classes, "is_package": s.is_package,
            "sort_order": s.sort_order, "is_active": s.is_active,
            "prices": [{"id": p.id, "car_class": p.car_class, "package_name": p.package_name,
                        "price_from": float(p.price_from), "price_to": float(p.price_to) if p.price_to else None,
                        "description": p.description} for p in s.prices],
        }
        for s in services
    ]


@router.post("/services")
async def create_service(data: ServiceData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    service = Service(**data.model_dump())
    session.add(service)
    await session.commit()
    await session.refresh(service)
    return {"id": service.id, "name": service.name}


@router.put("/services/{service_id}")
async def update_service(service_id: int, data: ServiceData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    service = await session.get(Service, service_id)
    if not service:
        return {"error": "Not found"}
    for k, v in data.model_dump().items():
        setattr(service, k, v)
    await session.commit()
    return {"id": service.id, "name": service.name}


# Prices CRUD
@router.post("/prices")
async def create_price(data: PriceData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    price = ServicePrice(
        service_id=data.service_id,
        car_class=data.car_class,
        package_name=data.package_name,
        price_from=Decimal(str(data.price_from)),
        price_to=Decimal(str(data.price_to)) if data.price_to else None,
        description=data.description,
    )
    session.add(price)
    await session.commit()
    return {"id": price.id}


@router.put("/prices/{price_id}")
async def update_price(price_id: int, data: PriceData, _: User = Depends(get_admin_user), session: AsyncSession = Depends(get_session)):
    price = await session.get(ServicePrice, price_id)
    if not price:
        return {"error": "Not found"}
    price.price_from = Decimal(str(data.price_from))
    price.price_to = Decimal(str(data.price_to)) if data.price_to else None
    price.car_class = data.car_class
    price.package_name = data.package_name
    price.description = data.description
    await session.commit()
    return {"id": price.id}
