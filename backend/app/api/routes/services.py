from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import ServiceCategory, Service

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("")
async def get_services(session: AsyncSession = Depends(get_session)):
    """Get all active service categories with their services."""
    result = await session.execute(
        select(ServiceCategory)
        .where(ServiceCategory.is_active == True)
        .options(selectinload(ServiceCategory.services).selectinload(Service.prices))
        .order_by(ServiceCategory.sort_order)
    )
    categories = result.scalars().unique().all()

    return [
        {
            "id": cat.id,
            "name": cat.name,
            "icon": cat.icon,
            "description": cat.description,
            "services": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "duration_min_hours": float(s.duration_min_hours),
                    "duration_max_hours": float(s.duration_max_hours),
                    "has_car_classes": s.has_car_classes,
                    "is_package": s.is_package,
                    "image_url": s.image_url,
                    "prices": [
                        {
                            "id": p.id,
                            "car_class": p.car_class,
                            "package_name": p.package_name,
                            "price_from": float(p.price_from),
                            "price_to": float(p.price_to) if p.price_to else None,
                            "description": p.description,
                        }
                        for p in s.prices
                    ],
                }
                for s in cat.services
                if s.is_active
            ],
        }
        for cat in categories
    ]


@router.get("/{service_id}")
async def get_service(service_id: int, session: AsyncSession = Depends(get_session)):
    """Get service details with prices."""
    result = await session.execute(
        select(Service)
        .where(Service.id == service_id, Service.is_active == True)
        .options(selectinload(Service.prices))
    )
    service = result.scalar_one_or_none()
    if not service:
        return {"error": "Service not found"}, 404

    return {
        "id": service.id,
        "category_id": service.category_id,
        "name": service.name,
        "description": service.description,
        "duration_min_hours": float(service.duration_min_hours),
        "duration_max_hours": float(service.duration_max_hours),
        "has_car_classes": service.has_car_classes,
        "is_package": service.is_package,
        "image_url": service.image_url,
        "prices": [
            {
                "id": p.id,
                "car_class": p.car_class,
                "package_name": p.package_name,
                "price_from": float(p.price_from),
                "price_to": float(p.price_to) if p.price_to else None,
                "description": p.description,
            }
            for p in service.prices
        ],
    }
