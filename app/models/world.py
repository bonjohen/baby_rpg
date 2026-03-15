import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow():
    return datetime.now(timezone.utc)


def _new_id():
    return str(uuid.uuid4())


class World(Base):
    __tablename__ = "worlds"

    world_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    world_name: Mapped[str] = mapped_column(String(100), nullable=False)
    world_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_version: Mapped[str] = mapped_column(String(20), default="0.1.0")
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    zones: Mapped[list["Zone"]] = relationship(back_populates="world", cascade="all, delete-orphan")


class Zone(Base):
    __tablename__ = "zones"

    zone_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    world_id: Mapped[str] = mapped_column(String(36), ForeignKey("worlds.world_id"), nullable=False)
    zone_name: Mapped[str] = mapped_column(String(100), nullable=False)
    zone_type: Mapped[str] = mapped_column(String(50), default="overworld")
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    terrain_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    adjacency: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string of zone transitions

    world: Mapped["World"] = relationship(back_populates="zones")
    tiles: Mapped[list["Tile"]] = relationship(back_populates="zone", cascade="all, delete-orphan")


class Tile(Base):
    __tablename__ = "tiles"

    tile_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    zone_id: Mapped[str] = mapped_column(String(36), ForeignKey("zones.zone_id"), nullable=False)
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    terrain_type: Mapped[str] = mapped_column(String(30), default="grass")
    passable: Mapped[bool] = mapped_column(Boolean, default=True)
    movement_cost: Mapped[float] = mapped_column(Float, default=1.0)

    zone: Mapped["Zone"] = relationship(back_populates="tiles")
