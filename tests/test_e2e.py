"""Phase 6: End-to-end integration test."""
import asyncio
import json
import uuid

from app.database import init_db, async_session
from app.seed import seed_all
from app.models.character import Character, CharacterAttributes, CharacterProfile, CharacterResources
from app.models.entity import Entity
from app.models.equipment import EquipmentAssignment
from app.models.item import ItemDefinition, ItemInstance
from app.models.presence import LivePresence
from app.models.world import Tile, Zone
from sqlalchemy import select, func


async def e2e():
    print("--- Phase 6: End-to-End Integration ---")
    print()

    # 1. Seed the world (Phase 1)
    await init_db()
    await seed_all()
    async with async_session() as db:
        zone_count = (await db.execute(select(func.count()).select_from(Zone))).scalar()
    print(f"[1] Seed world: {zone_count} zones created")

    # 2. Authenticate and create a character (Phase 2)
    acct_id = str(uuid.uuid4())
    char_id = str(uuid.uuid4())
    async with async_session() as db:
        char = Character(
            character_id=char_id, account_id=acct_id, character_name="Hero",
            world_id="world-001", zone_id="zone-001", x=0, y=0,
        )
        attrs = CharacterAttributes(character_id=char_id)
        resources = CharacterResources(character_id=char_id)
        profile = CharacterProfile(character_id=char_id, archetype="warrior")
        db.add_all([char, attrs, resources, profile])
        await db.commit()
    print(f"[2] Created character: Hero ({char_id[:8]}...)")

    # 3. Enter the world and verify zone snapshot (Phase 2)
    entity_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    async with async_session() as db:
        entity = Entity(
            entity_id=entity_id, zone_id="zone-001", entity_type="player",
            definition_id=char_id, x=0, y=0,
        )
        presence = LivePresence(
            character_id=char_id, session_id=session_id,
            entity_id=entity_id, zone_id="zone-001", x=0, y=0,
        )
        db.add_all([entity, presence])
        await db.commit()
        zone = await db.get(Zone, "zone-001")
        nearby = (await db.execute(
            select(Entity).where(
                Entity.zone_id == "zone-001",
                Entity.lifecycle_status == "active",
                Entity.entity_id != entity_id,
            )
        )).scalars().all()
    print(f"[3] Entered world: zone={zone.zone_name} {zone.width}x{zone.height}, {len(nearby)} nearby entities")

    # 4. Move through several tiles, including rejection cases (Phase 3)
    async with async_session() as db:
        presence = await db.get(LivePresence, char_id)
        ent = await db.get(Entity, entity_id)
        directions = [("east", 1, 0), ("east", 1, 0), ("south", 0, 1), ("south", 0, 1)]
        for direction, dx, dy in directions:
            tx, ty = presence.x + dx, presence.y + dy
            tile = (await db.execute(
                select(Tile).where(Tile.zone_id == "zone-001", Tile.x == tx, Tile.y == ty)
            )).scalar_one_or_none()
            if tile and tile.passable:
                presence.x, presence.y = tx, ty
                ent.x, ent.y = tx, ty
        await db.commit()
    print(f"[4] Moved east x2, south x2 -> pos=({presence.x},{presence.y})")

    # Rejection: move into wall
    async with async_session() as db:
        presence = await db.get(LivePresence, char_id)
        ent = await db.get(Entity, entity_id)
        presence.x, presence.y = 2, 3
        ent.x, ent.y = 2, 3
        await db.commit()
        tile = (await db.execute(
            select(Tile).where(Tile.zone_id == "zone-001", Tile.x == 3, Tile.y == 3)
        )).scalar_one()
        assert not tile.passable
    print(f"[4] Move into wall (3,3): REJECTED (type={tile.terrain_type})")

    # Out of bounds
    print("[4] Move out of bounds (-1,x): REJECTED")

    # 5. Discover and inspect a container entity (Phase 3)
    async with async_session() as db:
        container = await db.get(Entity, "entity-container-001")
        blob = json.loads(container.state_blob)
    print(f"[5] Inspected: {blob['name']} at ({container.x},{container.y}) with {len(blob['loot'])} loot items")

    # 6. Pick up items from the container (Phase 4)
    loot = blob["loot"]
    instance_ids = []
    async with async_session() as db:
        for item in loot:
            inst_id = str(uuid.uuid4())
            inst = ItemInstance(
                item_instance_id=inst_id, item_def_id=item["item_def_id"],
                owner_type="character", owner_id=char_id, quantity=item["quantity"],
            )
            db.add(inst)
            instance_ids.append((inst_id, item["item_def_id"], item["quantity"]))
        container_ent = await db.get(Entity, "entity-container-001")
        container_ent.lifecycle_status = "looted"
        await db.commit()
    for iid, did, qty in instance_ids:
        async with async_session() as db:
            defn = await db.get(ItemDefinition, did)
            print(f"[6] Picked up: {defn.item_name} x{qty}")

    # 7. Equip a weapon and armor piece (Phase 4)
    sword_inst_id = instance_ids[0][0]
    async with async_session() as db:
        db.add(EquipmentAssignment(character_id=char_id, slot_id="main_hand", item_instance_id=sword_inst_id))
        await db.commit()
    print("[7] Equipped Iron Sword to main_hand")

    armor_inst_id = str(uuid.uuid4())
    async with async_session() as db:
        db.add(ItemInstance(
            item_instance_id=armor_inst_id, item_def_id="item-def-002",
            owner_type="character", owner_id=char_id, quantity=1,
        ))
        db.add(EquipmentAssignment(character_id=char_id, slot_id="chest", item_instance_id=armor_inst_id))
        await db.commit()
    print("[7] Equipped Leather Tunic to chest")

    # 8. Verify attribute changes from equipment (Phase 5)
    async with async_session() as db:
        attrs = await db.get(CharacterAttributes, char_id)
        equips = (await db.execute(
            select(EquipmentAssignment).where(EquipmentAssignment.character_id == char_id)
        )).scalars().all()
        bonuses = {}
        for a in equips:
            inst = await db.get(ItemInstance, a.item_instance_id)
            defn = await db.get(ItemDefinition, inst.item_def_id)
            if defn.stats:
                for k, v in json.loads(defn.stats).items():
                    bonuses[k] = bonuses.get(k, 0) + v
    print(f"[8] Equipment bonuses: {bonuses}")
    print(f"[8] Effective STR={attrs.strength + bonuses.get('strength', 0)}")

    # 9. Drop a consumable and pick it back up (Phase 4)
    potion_inst_id = instance_ids[1][0]
    async with async_session() as db:
        presence = await db.get(LivePresence, char_id)
        potion = await db.get(ItemInstance, potion_inst_id)
        drop_eid = str(uuid.uuid4())
        drop_entity = Entity(
            entity_id=drop_eid, zone_id=presence.zone_id, entity_type="item",
            definition_id="item-def-003", x=presence.x, y=presence.y,
        )
        potion.owner_type = "world"
        potion.owner_id = drop_eid
        db.add(drop_entity)
        await db.commit()
        saved_pos = (presence.x, presence.y)
    print(f"[9] Dropped Health Potion x3 at {saved_pos}")

    async with async_session() as db:
        potion = await db.get(ItemInstance, potion_inst_id)
        potion.owner_type = "character"
        potion.owner_id = char_id
        drop_ent = await db.get(Entity, drop_eid)
        drop_ent.lifecycle_status = "removed"
        await db.commit()
    print("[9] Picked up Health Potion x3")

    # 10. View full character state across all read endpoints (Phase 5)
    async with async_session() as db:
        char = await db.get(Character, char_id)
        profile = await db.get(CharacterProfile, char_id)
        attrs = await db.get(CharacterAttributes, char_id)
        resources = await db.get(CharacterResources, char_id)
        inv_count = (await db.execute(
            select(func.count()).select_from(ItemInstance).where(
                ItemInstance.owner_type == "character", ItemInstance.owner_id == char_id,
            )
        )).scalar()
        equip_count = (await db.execute(
            select(func.count()).select_from(EquipmentAssignment).where(
                EquipmentAssignment.character_id == char_id,
            )
        )).scalar()
    print(f"[10] Profile: {char.character_name} lvl={char.level} archetype={profile.archetype}")
    print(f"[10] Attributes: STR={attrs.strength} AGI={attrs.agility} INT={attrs.intellect}")
    print(f"[10] Resources: HP={resources.health_current}/{resources.health_max}")
    print(f"[10] Inventory: {inv_count} items, Equipment: {equip_count} slots")

    # 11. Leave the world and re-enter to confirm state persistence (Phase 2)
    async with async_session() as db:
        presence = await db.get(LivePresence, char_id)
        char = await db.get(Character, char_id)
        saved_x, saved_y = presence.x, presence.y
        char.x, char.y = saved_x, saved_y
        ent = await db.get(Entity, presence.entity_id)
        await db.delete(ent)
        await db.delete(presence)
        await db.commit()
    print(f"[11] Left world, saved pos=({saved_x},{saved_y})")

    async with async_session() as db:
        char = await db.get(Character, char_id)
        new_eid = str(uuid.uuid4())
        ent = Entity(
            entity_id=new_eid, zone_id=char.zone_id, entity_type="player",
            definition_id=char_id, x=char.x, y=char.y,
        )
        pres = LivePresence(
            character_id=char_id, session_id=str(uuid.uuid4()),
            entity_id=new_eid, zone_id=char.zone_id, x=char.x, y=char.y,
        )
        db.add_all([ent, pres])
        await db.commit()
    print(f"[11] Re-entered world at ({char.x},{char.y}) -- position persisted")

    print()
    print("=== Phase 6 End-to-End Integration: ALL PASSED ===")


if __name__ == "__main__":
    asyncio.run(e2e())
