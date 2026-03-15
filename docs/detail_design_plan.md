# Minimum Demo Implementation Plan

This plan identifies the smallest set of functions needed to demonstrate the core behavior loops described in the design document: character creation, world entry, movement with server validation, inventory/equipment management, and entity visibility. Combat is explicitly deferred per the MVP boundary.

## Tech Stack

- **Language**: Python
- **Database**: SQLite (via SQLAlchemy ORM + aiosqlite for async)
- **Server framework**: FastAPI
- **Validation**: Pydantic v2 (ships with FastAPI)

## Project Structure

```
baby_rpg/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── world.py         # World, Zone, Tile
│   │   ├── entity.py        # Entity
│   │   ├── item.py          # ItemDefinition, ItemInstance
│   │   ├── character.py     # Character, CharacterAttributes, CharacterResources
│   │   ├── equipment.py     # EquipmentAssignment
│   │   └── presence.py      # LivePresence
│   ├── schemas/             # Pydantic request/response schemas
│   │   └── ...
│   ├── routers/             # FastAPI route modules
│   │   └── ...
│   └── seed.py              # Seed data functions
├── tests/
│   └── ...
├── requirements.txt
└── docs/
```

## Guiding Principles

- Server is source of truth; client sends intents, server validates and returns results.
- Definition data (static) is separated from instance data (runtime).
- Every function listed is needed to complete at least one demonstrable user flow.

---

## Phase 1: Foundation — Data Models & Seed Data

Establish the storage layer and populate a playable demo world. Nothing runs without this.

### Project Setup

[X] Create `requirements.txt` (fastapi, uvicorn, sqlalchemy, aiosqlite, pydantic)
[X] Create `app/__init__.py`, `app/models/__init__.py`
[X] Create `app/database.py` — async SQLAlchemy engine, sessionmaker, declarative Base
[X] Create `app/main.py` — FastAPI app with lifespan event that creates tables

### Data Models

[X] Define `World` model in `app/models/world.py` (world_id, world_name, content_version, status)
[X] Define `Zone` model in `app/models/world.py` (zone_id, world_id, width, height, terrain_ref, adjacency)
[X] Define `Tile` model in `app/models/world.py` (zone_id, x, y, terrain_type, passable, movement_cost)
[X] Define `Entity` model in `app/models/entity.py` (entity_id, zone_id, entity_type, definition_id, x, y, facing, state_blob)
[X] Define `ItemDefinition` model in `app/models/item.py` (item_def_id, item_name, category, stackable, equipment_slot_rules, stats)
[X] Define `ItemInstance` model in `app/models/item.py` (item_instance_id, item_def_id, owner_type, owner_id, quantity)
[X] Define `Character` model in `app/models/character.py` (character_id, account_id, character_name, world_id, zone_id, x, y, level, experience)
[X] Define `CharacterAttributes` model in `app/models/character.py` (character_id, strength, agility, intellect, endurance, willpower)
[X] Define `CharacterResources` model in `app/models/character.py` (character_id, health_current, health_max, mana_current, mana_max)
[X] Define `EquipmentAssignment` model in `app/models/equipment.py` (character_id, slot_id, item_instance_id)
[X] Define `LivePresence` model in `app/models/presence.py` (character_id, session_id, entity_id, zone_id, x, y, connection_state)

### Seed & Bootstrap Functions

[X] Implement `seed_world` — create one world with 2–3 small zones and basic tile grids (grass, wall, water); populate adjacency
[X] Implement `seed_item_definitions` — create a small catalog: a weapon, a piece of armor, and a consumable
[X] Implement `seed_entities` — place a few static NPCs and a lootable container in a zone
[X] Run seed functions and verify data is queryable

### Phase 1 Validation

[X] Confirm all models can be created, read, and persisted
[X] Confirm seed data produces a coherent world with zones, tiles, items, and entities

---

## Phase 2: Character Lifecycle — Creation Through World Entry

Build the path from login to standing on the map. This is the first end-to-end user flow.

### Functions

[X] Implement `authenticate` — validate credentials, return session_token and account_id (stub acceptable)
[X] Implement `list_characters` — return all characters belonging to an account
[X] Implement `create_character` — create character, attributes, and resources with starting values; assign to default world/zone/position
[X] Implement `load_character` — return character record, attributes, resources, skill list, inventory, and equipment in one response
[X] Implement `enter_world` — create LivePresence and world Entity for the character; return zone terrain, nearby entities, and starting position
[X] Implement `leave_world` — save position, remove LivePresence and world Entity

### Phase 2 Validation — Demo Flow: Character Creation and World Entry

[X] `authenticate` → `create_character` → `enter_world` → verify character exists in zone with correct position
[X] `leave_world` → verify LivePresence and Entity are removed, position is saved
[X] `authenticate` → `list_characters` → `load_character` → `enter_world` → verify returning character resumes at saved position

---

## Phase 3: World Interaction — Movement and Entity Visibility

Demonstrate the intent-validate-result loop. The character moves through the world and sees what is nearby.

### Functions

[X] Implement `get_zone` — return zone metadata and tile data for rendering
[X] Implement `attempt_move` — validate terrain passability, bounds, and movement rules; update entity and live_presence position on success; return accepted/rejected with new coordinates
[X] Implement `get_nearby_entities` — return entities visible from a given position within a radius
[X] Implement `get_entity` — return full entity state including state_blob for inspect/interact targeting

### Phase 3 Validation — Demo Flow: Movement

[X] Move character through passable tiles and confirm position updates
[X] Attempt move into wall/water tile and confirm rejection
[X] Attempt move out of zone bounds and confirm rejection
[X] Move character near seeded NPCs/containers and confirm they appear in `get_nearby_entities`
[X] Inspect a seeded entity with `get_entity` and confirm state_blob is returned

---

## Phase 4: Inventory and Equipment — Item Ownership and the Equip Cycle

Demonstrate item transfers between world, inventory, and equipment slots.

### Functions

[X] Implement `get_inventory` — return all item instances owned by the character (owner_type=character)
[X] Implement `add_item_to_inventory` — create or stack an item instance assigned to the character; respect stackable flag and max_stack_size
[X] Implement `drop_item` — change owner to world, create a dropped-item entity at the character's position; split stack if partial quantity
[X] Implement `pickup_item` — validate proximity, transfer item entity ownership to character inventory, remove world entity
[X] Implement `equip_item` — validate slot rules from item definition, swap existing item back to inventory if slot is occupied, create assignment
[X] Implement `unequip_item` — remove equipment assignment, return item to inventory

### Phase 4 Validation — Demo Flow: Item Pickup and Equip

[X] `pickup_item` from seeded container → `get_inventory` confirms item in inventory
[X] `equip_item` to appropriate slot → `get_equipment` confirms item in slot
[X] `unequip_item` → item returns to inventory, slot is empty
[X] Equip a second item to an occupied slot → first item swaps back to inventory
[X] Reject equip when item definition slot rules do not match target slot

### Phase 4 Validation — Demo Flow: Item Drop and Retrieval

[X] `drop_item` → item entity appears at character's position on the map
[X] `get_nearby_entities` confirms dropped item is visible
[X] `pickup_item` to retrieve → item returns to inventory, world entity removed
[X] Drop partial stack → original stack reduced, new world entity has correct quantity

---

## Phase 5: Character State Reads — Management UI Support

Expose all character data needed by profile, attributes, resources, skills, and equipment pages.

### Functions

[ ] Implement `get_character_profile` — return identity, level, experience, and presentation fields
[ ] Implement `get_character_attributes` — return base attributes and compute derived values from equipment and effects
[ ] Implement `get_character_resources` — return current and max resource pools
[ ] Implement `get_character_skills` — return learned skills with rank, slot assignment, and learned state
[ ] Implement `get_equipment` — return all equipment assignments with resolved item details

### Phase 5 Validation — Demo Flow: Character Inspection

[ ] All five read functions return correct data for a freshly created character
[ ] `get_character_attributes` reflects stat changes after equipping/unequipping an item
[ ] `get_equipment` returns item definition details alongside slot assignments, not just instance IDs

---

## Phase 6: End-to-End Integration

Run the complete demo scenario as a single continuous sequence to confirm all phases work together.

[ ] Seed the world (Phase 1)
[ ] Authenticate and create a character (Phase 2)
[ ] Enter the world and verify zone snapshot (Phase 2)
[ ] Move through several tiles, including rejection cases (Phase 3)
[ ] Discover and inspect a container entity (Phase 3)
[ ] Pick up items from the container (Phase 4)
[ ] Equip a weapon and armor piece (Phase 4)
[ ] Verify attribute changes from equipment (Phase 5)
[ ] Drop a consumable and pick it back up (Phase 4)
[ ] View full character state across all read endpoints (Phase 5)
[ ] Leave the world and re-enter to confirm state persistence (Phase 2)

---

## What Is Intentionally Excluded

Per the design document's MVP boundary and the goal of a minimum demo:

- **Combat**: Same intent-validate-result model as movement; deferred until movement and world interaction are stable.
- **Realtime event channel / WebSocket**: Demo uses request-response only. The event model can be layered on top of these same functions later.
- **Skills transactional operations**: Learning, ranking up, and slotting skills. Read-only skill display is included.
- **Trading / vendor**: Variant of inventory ownership transfer; deferred.
- **Quest / journal system**: Read-only display deferred; no quest state machine.
- **Chat**: Deferred; does not affect core game state.
- **Multi-account / concurrent sessions**: Demo assumes single-player interaction against the server.
- **Content versioning and cache sync**: Noted in design but not required for a local demo.
