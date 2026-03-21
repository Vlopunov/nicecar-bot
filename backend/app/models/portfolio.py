from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("service_categories.id"), nullable=True)
    service_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("services.id"), nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    image_before_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    car_brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    car_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    category = relationship("ServiceCategory", lazy="selectin")
    service = relationship("Service", lazy="selectin")
