from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.world import _utcnow


class EquipmentAssignment(Base):
    __tablename__ = "equipment_assignments"

    character_id: Mapped[str] = mapped_column(String(36), ForeignKey("characters.character_id"), primary_key=True)
    slot_id: Mapped[str] = mapped_column(String(30), primary_key=True)  # head, chest, legs, feet, main_hand, off_hand, etc.
    item_instance_id: Mapped[str] = mapped_column(String(36), nullable=False)
    equipped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    state: Mapped[str] = mapped_column(String(20), default="equipped")
