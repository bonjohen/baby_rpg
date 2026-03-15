# Baby RPG

A client-server multiplayer RPG where players share a common map and interact through a central game service. The server is the source of truth — clients send intents, the server validates and returns results.

## Status

MVP demo is functional. The server supports character creation, tile-based movement with terrain validation, inventory/equipment management, and full character state reads. See `docs/detail_design_plan.md` for the implementation roadmap.

## Tech Stack

- **Python** with **FastAPI**
- **SQLite** via SQLAlchemy (async, aiosqlite)
- **Pydantic v2** for request/response validation

## Setup

```bash
pip install -r requirements.txt
```

## Running

```bash
uvicorn app.main:app --reload
```

The server auto-creates the database and seeds demo data on first startup. Interactive API docs are available at `http://localhost:8000/docs`.

## Running the Integration Test

```bash
PYTHONPATH=. python tests/test_e2e.py
```

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Stub authentication (creates account on first login) |

### Characters
| Method | Path | Description |
|--------|------|-------------|
| GET | `/characters/?account_id=` | List characters for an account |
| POST | `/characters/` | Create a new character |
| GET | `/characters/{id}` | Load full character state |
| POST | `/characters/{id}/enter` | Enter the world (creates entity + presence) |
| POST | `/characters/{id}/leave` | Leave the world (saves position, cleans up) |

### Character State
| Method | Path | Description |
|--------|------|-------------|
| GET | `/characters/{id}/profile` | Identity, level, archetype |
| GET | `/characters/{id}/attributes` | Base + equipment-derived stats |
| GET | `/characters/{id}/resources` | HP, mana, stamina pools |
| GET | `/characters/{id}/skills` | Learned skills (MVP stub) |

### Inventory & Equipment
| Method | Path | Description |
|--------|------|-------------|
| GET | `/characters/{id}/inventory` | List inventory items |
| POST | `/characters/{id}/inventory` | Add item to inventory |
| POST | `/characters/{id}/inventory/{item_id}/drop` | Drop item into world |
| POST | `/characters/{id}/pickup/{entity_id}` | Pick up item from world |
| POST | `/characters/{id}/equip` | Equip item to slot |
| DELETE | `/characters/{id}/equip/{slot_id}` | Unequip item |
| GET | `/characters/{id}/equipment` | List equipped items |

### World
| Method | Path | Description |
|--------|------|-------------|
| GET | `/world/zones/{zone_id}` | Zone metadata + terrain grid |
| POST | `/world/characters/{id}/move` | Attempt movement (validates terrain) |
| GET | `/world/zones/{zone_id}/entities?x=&y=&radius=` | Nearby entities |
| GET | `/world/entities/{entity_id}` | Inspect entity details |

## Seed Data

The server starts with:
- **1 world** (Eldoria) with **3 zones**: Village Green (10x10), Dark Forest (12x12), Cave Entrance (8x8)
- **3 item definitions**: Iron Sword, Leather Tunic, Health Potion
- **3 entities**: Elder Maren (NPC), Merchant Tova (NPC), Old Chest (lootable container)

## Project Structure

```
app/
├── main.py              # FastAPI app entry point
├── database.py          # Async SQLAlchemy engine + session
├── seed.py              # Demo world/item/entity seed data
├── models/              # SQLAlchemy ORM models
│   ├── world.py         # World, Zone, Tile
│   ├── entity.py        # Entity (players, NPCs, items on map)
│   ├── item.py          # ItemDefinition, ItemInstance
│   ├── character.py     # Character, Attributes, Resources, Profile
│   ├── equipment.py     # EquipmentAssignment
│   └── presence.py      # LivePresence (session state)
├── schemas/             # Pydantic request/response models
│   ├── auth.py
│   ├── character.py
│   ├── world.py
│   └── inventory.py
└── routers/             # FastAPI route handlers
    ├── auth.py
    ├── characters.py
    ├── character_state.py
    ├── inventory.py
    └── world.py
tests/
└── test_e2e.py          # End-to-end integration test
docs/
├── detail_design_document.md   # Product design spec
└── detail_design_plan.md       # Phased implementation plan
```
