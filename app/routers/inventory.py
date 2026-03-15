import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.entity import Entity
from app.models.equipment import EquipmentAssignment
from app.models.item import ItemDefinition, ItemInstance
from app.models.presence import LivePresence
from app.schemas.inventory import (
    AddItemRequest,
    DropItemRequest,
    EquipmentDetail,
    EquipRequest,
    ItemInstanceDetail,
)

router = APIRouter(prefix="/characters/{character_id}", tags=["inventory"])


@router.get("/inventory", response_model=list[ItemInstanceDetail])
async def get_inventory(character_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ItemInstance, ItemDefinition).join(
            ItemDefinition, ItemInstance.item_def_id == ItemDefinition.item_def_id
        ).where(
            ItemInstance.owner_type == "character",
            ItemInstance.owner_id == character_id,
        )
    )
    return [
        ItemInstanceDetail(
            item_instance_id=inst.item_instance_id,
            item_def_id=inst.item_def_id,
            item_name=defn.item_name,
            item_category=defn.item_category,
            quantity=inst.quantity,
            owner_type=inst.owner_type,
            owner_id=inst.owner_id,
        )
        for inst, defn in result.all()
    ]


@router.post("/inventory", response_model=ItemInstanceDetail)
async def add_item_to_inventory(character_id: str, req: AddItemRequest, db: AsyncSession = Depends(get_db)):
    defn = await db.get(ItemDefinition, req.item_def_id)
    if not defn:
        raise HTTPException(status_code=404, detail="Item definition not found")

    # If stackable, try to add to existing stack
    if defn.stackable:
        result = await db.execute(
            select(ItemInstance).where(
                ItemInstance.item_def_id == req.item_def_id,
                ItemInstance.owner_type == "character",
                ItemInstance.owner_id == character_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            new_qty = min(existing.quantity + req.quantity, defn.max_stack_size)
            existing.quantity = new_qty
            await db.commit()
            return ItemInstanceDetail(
                item_instance_id=existing.item_instance_id,
                item_def_id=existing.item_def_id,
                item_name=defn.item_name,
                item_category=defn.item_category,
                quantity=existing.quantity,
                owner_type=existing.owner_type,
                owner_id=existing.owner_id,
            )

    instance = ItemInstance(
        item_instance_id=str(uuid.uuid4()),
        item_def_id=req.item_def_id,
        owner_type="character",
        owner_id=character_id,
        quantity=req.quantity,
    )
    db.add(instance)
    await db.commit()

    return ItemInstanceDetail(
        item_instance_id=instance.item_instance_id,
        item_def_id=instance.item_def_id,
        item_name=defn.item_name,
        item_category=defn.item_category,
        quantity=instance.quantity,
        owner_type=instance.owner_type,
        owner_id=instance.owner_id,
    )


@router.post("/inventory/{item_instance_id}/drop", response_model=dict)
async def drop_item(character_id: str, item_instance_id: str, req: DropItemRequest, db: AsyncSession = Depends(get_db)):
    instance = await db.get(ItemInstance, item_instance_id)
    if not instance or instance.owner_type != "character" or instance.owner_id != character_id:
        raise HTTPException(status_code=404, detail="Item not in inventory")

    presence = await db.get(LivePresence, character_id)
    if not presence:
        raise HTTPException(status_code=400, detail="Character is not in the world")

    drop_qty = req.quantity if req.quantity is not None else instance.quantity

    if drop_qty <= 0 or drop_qty > instance.quantity:
        raise HTTPException(status_code=400, detail="Invalid quantity")

    # Create world entity for dropped item
    drop_entity_id = str(uuid.uuid4())
    drop_entity = Entity(
        entity_id=drop_entity_id,
        zone_id=presence.zone_id,
        entity_type="item",
        definition_id=instance.item_def_id,
        x=presence.x,
        y=presence.y,
        state_blob=json.dumps({"item_instance_id": item_instance_id, "quantity": drop_qty}),
    )
    db.add(drop_entity)

    if drop_qty == instance.quantity:
        # Drop entire stack — transfer ownership to world
        instance.owner_type = "world"
        instance.owner_id = drop_entity_id
    else:
        # Partial drop — split stack
        instance.quantity -= drop_qty
        new_instance = ItemInstance(
            item_instance_id=str(uuid.uuid4()),
            item_def_id=instance.item_def_id,
            owner_type="world",
            owner_id=drop_entity_id,
            quantity=drop_qty,
        )
        db.add(new_instance)

    await db.commit()
    return {"status": "dropped", "entity_id": drop_entity_id, "x": presence.x, "y": presence.y, "quantity": drop_qty}


@router.post("/pickup/{entity_id}", response_model=ItemInstanceDetail)
async def pickup_item(character_id: str, entity_id: str, db: AsyncSession = Depends(get_db)):
    presence = await db.get(LivePresence, character_id)
    if not presence:
        raise HTTPException(status_code=400, detail="Character is not in the world")

    entity = await db.get(Entity, entity_id)
    if not entity or entity.entity_type != "item" or entity.lifecycle_status != "active":
        raise HTTPException(status_code=404, detail="No pickupable item entity found")

    # Proximity check
    if abs(entity.x - presence.x) > 1 or abs(entity.y - presence.y) > 1:
        raise HTTPException(status_code=400, detail="Too far away to pick up")

    # Find the item instance owned by this world entity
    result = await db.execute(
        select(ItemInstance).where(
            ItemInstance.owner_type == "world",
            ItemInstance.owner_id == entity_id,
        )
    )
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="No item instance for this entity")

    defn = await db.get(ItemDefinition, instance.item_def_id)

    # Transfer to character
    instance.owner_type = "character"
    instance.owner_id = character_id

    # If stackable, merge with existing
    if defn.stackable:
        existing_result = await db.execute(
            select(ItemInstance).where(
                ItemInstance.item_def_id == instance.item_def_id,
                ItemInstance.owner_type == "character",
                ItemInstance.owner_id == character_id,
                ItemInstance.item_instance_id != instance.item_instance_id,
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            existing.quantity = min(existing.quantity + instance.quantity, defn.max_stack_size)
            await db.delete(instance)
            instance = existing

    # Remove world entity
    entity.lifecycle_status = "removed"
    await db.commit()

    return ItemInstanceDetail(
        item_instance_id=instance.item_instance_id,
        item_def_id=instance.item_def_id,
        item_name=defn.item_name,
        item_category=defn.item_category,
        quantity=instance.quantity,
        owner_type=instance.owner_type,
        owner_id=instance.owner_id,
    )


@router.post("/equip", response_model=EquipmentDetail)
async def equip_item(character_id: str, req: EquipRequest, db: AsyncSession = Depends(get_db)):
    instance = await db.get(ItemInstance, req.item_instance_id)
    if not instance or instance.owner_type != "character" or instance.owner_id != character_id:
        raise HTTPException(status_code=404, detail="Item not in inventory")

    defn = await db.get(ItemDefinition, instance.item_def_id)
    if not defn.equipment_slot_rules:
        raise HTTPException(status_code=400, detail="Item cannot be equipped")

    allowed_slots = json.loads(defn.equipment_slot_rules)
    if req.slot_id not in allowed_slots:
        raise HTTPException(status_code=400, detail=f"Item cannot go in slot '{req.slot_id}'. Allowed: {allowed_slots}")

    # Check if slot is occupied — swap back to inventory
    existing_result = await db.execute(
        select(EquipmentAssignment).where(
            EquipmentAssignment.character_id == character_id,
            EquipmentAssignment.slot_id == req.slot_id,
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        await db.delete(existing)

    assignment = EquipmentAssignment(
        character_id=character_id,
        slot_id=req.slot_id,
        item_instance_id=req.item_instance_id,
    )
    db.add(assignment)
    await db.commit()

    stats = json.loads(defn.stats) if defn.stats else None
    return EquipmentDetail(
        slot_id=req.slot_id,
        item_instance_id=req.item_instance_id,
        item_name=defn.item_name,
        item_category=defn.item_category,
        stats=stats,
    )


@router.delete("/equip/{slot_id}", response_model=dict)
async def unequip_item(character_id: str, slot_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EquipmentAssignment).where(
            EquipmentAssignment.character_id == character_id,
            EquipmentAssignment.slot_id == slot_id,
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Nothing equipped in that slot")

    await db.delete(assignment)
    await db.commit()

    return {"status": "unequipped", "slot_id": slot_id, "item_instance_id": assignment.item_instance_id}


@router.get("/equipment", response_model=list[EquipmentDetail])
async def get_equipment(character_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EquipmentAssignment).where(EquipmentAssignment.character_id == character_id)
    )
    assignments = result.scalars().all()

    details = []
    for a in assignments:
        instance = await db.get(ItemInstance, a.item_instance_id)
        defn = await db.get(ItemDefinition, instance.item_def_id) if instance else None
        details.append(EquipmentDetail(
            slot_id=a.slot_id,
            item_instance_id=a.item_instance_id,
            item_name=defn.item_name if defn else None,
            item_category=defn.item_category if defn else None,
            stats=json.loads(defn.stats) if defn and defn.stats else None,
        ))
    return details
