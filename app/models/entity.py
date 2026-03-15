from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.world import _new_id, _utcnow


class Entity(Base):
    __tablename__ = "entities"

    entity_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    zone_id: Mapped[str] = mapped_column(String(36), ForeignKey("zones.zone_id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)  # player, npc, monster, item, container
    definition_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    facing: Mapped[str] = mapped_column(String(10), default="south")
    visibility_state: Mapped[str] = mapped_column(String(20), default="visible")
    state_blob: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON payload for type-specific state
    lifecycle_status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
