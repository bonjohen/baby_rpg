import json

from sqlalchemy import select

from app.database import async_session
from app.models.entity import Entity
from app.models.item import ItemDefinition
from app.models.world import Tile, World, Zone


async def seed_all():
    """Run all seed functions if the world doesn't already exist."""
    async with async_session() as session:
        existing = await session.execute(select(World).limit(1))
        if existing.scalar_one_or_none() is not None:
            return
    await seed_world()
    await seed_item_definitions()
    await seed_entities()


async def seed_world():
    """Create one world with 3 small zones and tile grids."""
    async with async_session() as session:
        world = World(
            world_id="world-001",
            world_name="Eldoria",
            world_description="A small starting world for new adventurers.",
        )
        session.add(world)

        # Zone definitions: name, type, width, height
        zone_specs = [
            ("zone-001", "Village Green", "town", 10, 10),
            ("zone-002", "Dark Forest", "wilderness", 12, 12),
            ("zone-003", "Cave Entrance", "dungeon", 8, 8),
        ]

        zones = []
        for zone_id, name, ztype, w, h in zone_specs:
            zone = Zone(
                zone_id=zone_id,
                world_id="world-001",
                zone_name=name,
                zone_type=ztype,
                width=w,
                height=h,
            )
            zones.append(zone)
            session.add(zone)

        # Set adjacency after creating zones
        zones[0].adjacency = json.dumps({"east": "zone-002"})
        zones[1].adjacency = json.dumps({"west": "zone-001", "north": "zone-003"})
        zones[2].adjacency = json.dumps({"south": "zone-002"})

        await session.flush()

        # Generate terrain tiles for each zone
        for zone in zones:
            for y in range(zone.height):
                for x in range(zone.width):
                    terrain_type, passable, cost = _tile_for(zone.zone_id, x, y, zone.width, zone.height)
                    tile = Tile(
                        zone_id=zone.zone_id,
                        x=x,
                        y=y,
                        terrain_type=terrain_type,
                        passable=passable,
                        movement_cost=cost,
                    )
                    session.add(tile)

        await session.commit()


def _tile_for(zone_id: str, x: int, y: int, w: int, h: int) -> tuple[str, bool, float]:
    """Determine tile type based on zone and position. Returns (terrain_type, passable, cost)."""
    # Borders are walls for cave
    if zone_id == "zone-003":
        if x == 0 or y == 0 or x == w - 1 or y == h - 1:
            return ("wall", False, 0.0)
        return ("stone", True, 1.0)

    # Forest has scattered trees and a water stream
    if zone_id == "zone-002":
        if x == 5 and y > 2:
            return ("water", False, 0.0)
        if (x + y) % 4 == 0 and x > 0 and y > 0:
            return ("tree", False, 0.0)
        return ("grass", True, 1.0)

    # Village green — mostly open, a few buildings (walls)
    if zone_id == "zone-001":
        if 3 <= x <= 5 and 3 <= y <= 5 and not (x == 4 and y == 5):
            return ("wall", False, 0.0)  # building with door at (4,5)
        return ("grass", True, 1.0)

    return ("grass", True, 1.0)


async def seed_item_definitions():
    """Create a small catalog: weapon, armor, consumable."""
    async with async_session() as session:
        items = [
            ItemDefinition(
                item_def_id="item-def-001",
                item_name="Iron Sword",
                item_category="weapon",
                rarity="common",
                stackable=False,
                max_stack_size=1,
                equipment_slot_rules=json.dumps(["main_hand"]),
                weight=3.0,
                value=50,
                stats=json.dumps({"attack": 5, "speed": 1.0}),
                description="A sturdy iron blade, good for beginners.",
            ),
            ItemDefinition(
                item_def_id="item-def-002",
                item_name="Leather Tunic",
                item_category="armor",
                rarity="common",
                stackable=False,
                max_stack_size=1,
                equipment_slot_rules=json.dumps(["chest"]),
                weight=2.0,
                value=30,
                stats=json.dumps({"defense": 3}),
                description="Simple leather armor offering light protection.",
            ),
            ItemDefinition(
                item_def_id="item-def-003",
                item_name="Health Potion",
                item_category="consumable",
                rarity="common",
                stackable=True,
                max_stack_size=10,
                use_rules=json.dumps({"effect": "heal", "amount": 25}),
                weight=0.5,
                value=10,
                description="Restores 25 health when consumed.",
            ),
        ]
        session.add_all(items)
        await session.commit()


async def seed_entities():
    """Place NPCs and a lootable container in the Village Green zone."""
    async with async_session() as session:
        entities = [
            Entity(
                entity_id="entity-npc-001",
                zone_id="zone-001",
                entity_type="npc",
                x=2,
                y=2,
                facing="south",
                state_blob=json.dumps({"name": "Elder Maren", "dialogue": "Welcome to Eldoria, young adventurer!"}),
            ),
            Entity(
                entity_id="entity-npc-002",
                zone_id="zone-001",
                entity_type="npc",
                x=7,
                y=7,
                facing="west",
                state_blob=json.dumps({"name": "Merchant Tova", "dialogue": "Looking to trade?"}),
            ),
            Entity(
                entity_id="entity-container-001",
                zone_id="zone-001",
                entity_type="container",
                x=6,
                y=1,
                state_blob=json.dumps({
                    "name": "Old Chest",
                    "loot": [
                        {"item_def_id": "item-def-001", "quantity": 1},
                        {"item_def_id": "item-def-003", "quantity": 3},
                    ],
                }),
            ),
        ]
        session.add_all(entities)
        await session.commit()
