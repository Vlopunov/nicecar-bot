from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ServiceCategory(Base):
    __tablename__ = "service_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[str] = mapped_column(String(10), nullable=False, default="🔧")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    services = relationship("Service", back_populates="category", lazy="selectin")


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("service_categories.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_min_hours: Mapped[float] = mapped_column(Numeric(5, 2), default=1.0)
    duration_max_hours: Mapped[float] = mapped_column(Numeric(5, 2), default=2.0)
    has_car_classes: Mapped[bool] = mapped_column(Boolean, default=False)
    is_package: Mapped[bool] = mapped_column(Boolean, default=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    category = relationship("ServiceCategory", back_populates="services")
    prices = relationship("ServicePrice", back_populates="service", lazy="selectin")


class ServicePrice(Base):
    __tablename__ = "service_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey("services.id"), nullable=False)
    car_class: Mapped[str | None] = mapped_column(String(10), nullable=True)  # I, II, III or null
    package_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    price_from: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    price_to: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    service = relationship("Service", back_populates="prices")
