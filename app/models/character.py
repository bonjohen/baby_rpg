from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.world import _new_id, _utcnow


class Character(Base):
    __tablename__ = "characters"

    character_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    account_id: Mapped[str] = mapped_column(String(36), nullable=False)
    character_name: Mapped[str] = mapped_column(String(50), nullable=False)
    avatar_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    world_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    zone_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    x: Mapped[int] = mapped_column(Integer, default=0)
    y: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    experience: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class CharacterAttributes(Base):
    __tablename__ = "character_attributes"

    character_id: Mapped[str] = mapped_column(String(36), ForeignKey("characters.character_id"), primary_key=True)
    strength: Mapped[int] = mapped_column(Integer, default=10)
    agility: Mapped[int] = mapped_column(Integer, default=10)
    intellect: Mapped[int] = mapped_column(Integer, default=10)
    endurance: Mapped[int] = mapped_column(Integer, default=10)
    willpower: Mapped[int] = mapped_column(Integer, default=10)


class CharacterResources(Base):
    __tablename__ = "character_resources"

    character_id: Mapped[str] = mapped_column(String(36), ForeignKey("characters.character_id"), primary_key=True)
    health_current: Mapped[int] = mapped_column(Integer, default=100)
    health_max: Mapped[int] = mapped_column(Integer, default=100)
    mana_current: Mapped[int] = mapped_column(Integer, default=50)
    mana_max: Mapped[int] = mapped_column(Integer, default=50)
    stamina_current: Mapped[int] = mapped_column(Integer, default=100)
    stamina_max: Mapped[int] = mapped_column(Integer, default=100)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class CharacterProfile(Base):
    __tablename__ = "character_profiles"

    character_id: Mapped[str] = mapped_column(String(36), ForeignKey("characters.character_id"), primary_key=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    faction: Mapped[str | None] = mapped_column(String(50), nullable=True)
    archetype: Mapped[str | None] = mapped_column(String(50), nullable=True)
    origin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    presentation_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
