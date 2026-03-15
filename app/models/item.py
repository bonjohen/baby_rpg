from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.world import _new_id, _utcnow


class ItemDefinition(Base):
    __tablename__ = "item_definitions"

    item_def_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    item_category: Mapped[str] = mapped_column(String(30), nullable=False)  # weapon, armor, consumable, misc
    rarity: Mapped[str] = mapped_column(String(20), default="common")
    stackable: Mapped[bool] = mapped_column(Boolean, default=False)
    max_stack_size: Mapped[int] = mapped_column(Integer, default=1)
    equipment_slot_rules: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: allowed slots
    use_rules: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: consumable effects
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    value: Mapped[int] = mapped_column(Integer, default=0)
    icon_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stats: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON: stat modifiers when equipped/used
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_version: Mapped[str] = mapped_column(String(20), default="0.1.0")


class ItemInstance(Base):
    __tablename__ = "item_instances"

    item_instance_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    item_def_id: Mapped[str] = mapped_column(String(36), nullable=False)
    owner_type: Mapped[str] = mapped_column(String(20), nullable=False)  # character, container, world
    owner_id: Mapped[str] = mapped_column(String(36), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    condition_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bound_state: Mapped[str | None] = mapped_column(String(20), nullable=True)
    custom_state: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
