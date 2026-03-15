import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.character import Character, CharacterAttributes, CharacterProfile, CharacterResources
from app.models.equipment import EquipmentAssignment
from app.models.item import ItemDefinition, ItemInstance

router = APIRouter(prefix="/characters/{character_id}", tags=["character_state"])


@router.get("/profile")
async def get_character_profile(character_id: str, db: AsyncSession = Depends(get_db)):
    character = await db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    profile = await db.get(CharacterProfile, character_id)

    return {
        "character_id": character.character_id,
        "character_name": character.character_name,
        "level": character.level,
        "experience": character.experience,
        "avatar_ref": character.avatar_ref,
        "archetype": profile.archetype if profile else None,
        "faction": profile.faction if profile else None,
        "origin": profile.origin if profile else None,
        "biography": profile.biography if profile else None,
    }


@router.get("/attributes")
async def get_character_attributes(character_id: str, db: AsyncSession = Depends(get_db)):
    attrs = await db.get(CharacterAttributes, character_id)
    if not attrs:
        raise HTTPException(status_code=404, detail="Character not found")

    base = {
        "strength": attrs.strength,
        "agility": attrs.agility,
        "intellect": attrs.intellect,
        "endurance": attrs.endurance,
        "willpower": attrs.willpower,
    }

    # Compute equipment bonuses
    bonuses = {"strength": 0, "agility": 0, "intellect": 0, "endurance": 0, "willpower": 0,
               "attack": 0, "defense": 0, "speed": 0}

    equip_result = await db.execute(
        select(EquipmentAssignment).where(EquipmentAssignment.character_id == character_id)
    )
    for assignment in equip_result.scalars().all():
        instance = await db.get(ItemInstance, assignment.item_instance_id)
        if not instance:
            continue
        defn = await db.get(ItemDefinition, instance.item_def_id)
        if not defn or not defn.stats:
            continue
        stats = json.loads(defn.stats)
        for key, val in stats.items():
            if key in bonuses:
                bonuses[key] += val

    # Derived totals
    effective = {k: base[k] + bonuses.get(k, 0) for k in base}

    return {
        "base": base,
        "equipment_bonuses": {k: v for k, v in bonuses.items() if v != 0},
        "effective": effective,
        "derived": {
            "attack": bonuses.get("attack", 0),
            "defense": bonuses.get("defense", 0),
            "speed": bonuses.get("speed", 0),
        },
    }


@router.get("/resources")
async def get_character_resources(character_id: str, db: AsyncSession = Depends(get_db)):
    resources = await db.get(CharacterResources, character_id)
    if not resources:
        raise HTTPException(status_code=404, detail="Character not found")

    return {
        "character_id": character_id,
        "health_current": resources.health_current,
        "health_max": resources.health_max,
        "mana_current": resources.mana_current,
        "mana_max": resources.mana_max,
        "stamina_current": resources.stamina_current,
        "stamina_max": resources.stamina_max,
    }


@router.get("/skills")
async def get_character_skills(character_id: str, db: AsyncSession = Depends(get_db)):
    # Skills are read-only stubs for the MVP — no skill definitions seeded yet
    character = await db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    return {
        "character_id": character_id,
        "skills": [],  # Empty until skill definitions and character_skill records are added
    }
