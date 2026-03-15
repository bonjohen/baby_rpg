from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.world import _new_id, _utcnow


class LivePresence(Base):
    __tablename__ = "live_presences"

    character_id: Mapped[str] = mapped_column(String(36), ForeignKey("characters.character_id"), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    zone_id: Mapped[str] = mapped_column(String(36), nullable=False)
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    facing: Mapped[str] = mapped_column(String(10), default="south")
    connection_state: Mapped[str] = mapped_column(String(20), default="connected")
    last_heartbeat_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    visibility_context: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
