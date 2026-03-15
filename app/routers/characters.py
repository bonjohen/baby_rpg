import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.character import Character, CharacterAttributes, CharacterProfile, CharacterResources
from app.models.entity import Entity
from app.models.equipment import EquipmentAssignment
from app.models.item import ItemInstance
from app.models.presence import LivePresence
from app.models.world import Zone
from app.schemas.character import (
    AttributesDetail,
    CharacterDetail,
    CharacterSummary,
    CreateCharacterRequest,
    EnterWorldResponse,
    EquipmentSlot,
    ResourcesDetail,
)

router = APIRouter(prefix="/characters", tags=["characters"])

DEFAULT_WORLD_ID = "world-001"
DEFAULT_ZONE_ID = "zone-001"
DEFAULT_X = 0
DEFAULT_Y = 0


@router.get("/", response_model=list[CharacterSummary])
async def list_characters(account_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Character).where(Character.account_id == account_id)
    )
    chars = result.scalars().all()
    summaries = []
    for c in chars:
        profile = await db.get(CharacterProfile, c.character_id)
        summaries.append(CharacterSummary(
            character_id=c.character_id,
            character_name=c.character_name,
            level=c.level,
            archetype=profile.archetype if profile else None,
            zone_id=c.zone_id,
        ))
    return summaries


@router.post("/", response_model=CharacterDetail)
async def create_character(req: CreateCharacterRequest, db: AsyncSession = Depends(get_db)):
    char_id = str(uuid.uuid4())
    character = Character(
        character_id=char_id,
        account_id=req.account_id,
        character_name=req.character_name,
        world_id=DEFAULT_WORLD_ID,
        zone_id=DEFAULT_ZONE_ID,
        x=DEFAULT_X,
        y=DEFAULT_Y,
    )
    attrs = CharacterAttributes(character_id=char_id)
    resources = CharacterResources(character_id=char_id)
    profile = CharacterProfile(character_id=char_id, archetype=req.archetype)

    db.add_all([character, attrs, resources, profile])
    await db.commit()

    return _build_detail(character, attrs, resources, [], 0)


@router.get("/{character_id}", response_model=CharacterDetail)
async def load_character(character_id: str, db: AsyncSession = Depends(get_db)):
    character = await db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    attrs = await db.get(CharacterAttributes, character_id)
    resources = await db.get(CharacterResources, character_id)

    equip_result = await db.execute(
        select(EquipmentAssignment).where(EquipmentAssignment.character_id == character_id)
    )
    equipment = equip_result.scalars().all()

    inv_count = (await db.execute(
        select(func.count()).select_from(ItemInstance).where(
            ItemInstance.owner_type == "character",
            ItemInstance.owner_id == character_id,
        )
    )).scalar() or 0

    equip_slots = []
    for e in equipment:
        equip_slots.append(EquipmentSlot(
            slot_id=e.slot_id,
            item_instance_id=e.item_instance_id,
        ))

    return _build_detail(character, attrs, resources, equip_slots, inv_count)


@router.post("/{character_id}/enter", response_model=EnterWorldResponse)
async def enter_world(character_id: str, session_id: str = "", db: AsyncSession = Depends(get_db)):
    character = await db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if not session_id:
        session_id = str(uuid.uuid4())

    # Create world entity for the character
    entity_id = str(uuid.uuid4())
    entity = Entity(
        entity_id=entity_id,
        zone_id=character.zone_id,
        entity_type="player",
        definition_id=character_id,
        x=character.x,
        y=character.y,
    )
    db.add(entity)

    # Create live presence
    presence = LivePresence(
        character_id=character_id,
        session_id=session_id,
        entity_id=entity_id,
        zone_id=character.zone_id,
        x=character.x,
        y=character.y,
    )
    db.add(presence)
    await db.commit()

    # Get zone info
    zone = await db.get(Zone, character.zone_id)

    # Get nearby entities
    nearby_result = await db.execute(
        select(Entity).where(
            Entity.zone_id == character.zone_id,
            Entity.entity_id != entity_id,
            Entity.lifecycle_status == "active",
        )
    )
    nearby = [
        {"entity_id": e.entity_id, "entity_type": e.entity_type, "x": e.x, "y": e.y}
        for e in nearby_result.scalars().all()
    ]

    return EnterWorldResponse(
        character_id=character_id,
        entity_id=entity_id,
        zone_id=character.zone_id,
        x=character.x,
        y=character.y,
        zone_width=zone.width,
        zone_height=zone.height,
        nearby_entities=nearby,
    )


@router.post("/{character_id}/leave")
async def leave_world(character_id: str, db: AsyncSession = Depends(get_db)):
    character = await db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Find and remove presence
    presence = await db.get(LivePresence, character_id)
    if not presence:
        raise HTTPException(status_code=400, detail="Character is not in the world")

    # Save position from presence back to character
    character.x = presence.x
    character.y = presence.y
    character.zone_id = presence.zone_id

    # Remove the player entity
    entity = await db.get(Entity, presence.entity_id)
    if entity:
        await db.delete(entity)

    await db.delete(presence)
    await db.commit()

    return {"status": "ok", "character_id": character_id}


def _build_detail(character, attrs, resources, equip_slots, inv_count):
    return CharacterDetail(
        character_id=character.character_id,
        account_id=character.account_id,
        character_name=character.character_name,
        level=character.level,
        experience=character.experience,
        world_id=character.world_id,
        zone_id=character.zone_id,
        x=character.x,
        y=character.y,
        attributes=AttributesDetail(
            strength=attrs.strength,
            agility=attrs.agility,
            intellect=attrs.intellect,
            endurance=attrs.endurance,
            willpower=attrs.willpower,
        ),
        resources=ResourcesDetail(
            health_current=resources.health_current,
            health_max=resources.health_max,
            mana_current=resources.mana_current,
            mana_max=resources.mana_max,
            stamina_current=resources.stamina_current,
            stamina_max=resources.stamina_max,
        ),
        equipment=equip_slots,
        inventory_count=inv_count,
    )
