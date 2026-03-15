import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.entity import Entity
from app.models.presence import LivePresence
from app.models.world import Tile, Zone
from app.schemas.world import EntityDetail, MoveRequest, MoveResult, TileDetail, ZoneDetail

router = APIRouter(prefix="/world", tags=["world"])

DIRECTION_DELTAS = {
    "north": (0, -1),
    "south": (0, 1),
    "east": (1, 0),
    "west": (-1, 0),
}


@router.get("/zones/{zone_id}", response_model=ZoneDetail)
async def get_zone(zone_id: str, db: AsyncSession = Depends(get_db)):
    zone = await db.get(Zone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    tile_result = await db.execute(
        select(Tile).where(Tile.zone_id == zone_id)
    )
    tiles = [
        TileDetail(x=t.x, y=t.y, terrain_type=t.terrain_type, passable=t.passable, movement_cost=t.movement_cost)
        for t in tile_result.scalars().all()
    ]

    adjacency = json.loads(zone.adjacency) if zone.adjacency else None

    return ZoneDetail(
        zone_id=zone.zone_id,
        zone_name=zone.zone_name,
        zone_type=zone.zone_type,
        width=zone.width,
        height=zone.height,
        adjacency=adjacency,
        tiles=tiles,
    )


@router.post("/characters/{character_id}/move", response_model=MoveResult)
async def attempt_move(character_id: str, req: MoveRequest, db: AsyncSession = Depends(get_db)):
    presence = await db.get(LivePresence, character_id)
    if not presence:
        raise HTTPException(status_code=400, detail="Character is not in the world")

    # Resolve target coordinates
    if req.direction:
        if req.direction not in DIRECTION_DELTAS:
            return MoveResult(accepted=False, x=presence.x, y=presence.y, reason=f"Invalid direction: {req.direction}")
        dx, dy = DIRECTION_DELTAS[req.direction]
        target_x = presence.x + dx
        target_y = presence.y + dy
    elif req.target_x is not None and req.target_y is not None:
        # Only allow single-tile moves
        dx = req.target_x - presence.x
        dy = req.target_y - presence.y
        if abs(dx) + abs(dy) != 1:
            return MoveResult(accepted=False, x=presence.x, y=presence.y, reason="Can only move one tile at a time")
        target_x, target_y = req.target_x, req.target_y
    else:
        return MoveResult(accepted=False, x=presence.x, y=presence.y, reason="Must provide direction or target coordinates")

    # Get zone for bounds check
    zone = await db.get(Zone, presence.zone_id)
    if target_x < 0 or target_x >= zone.width or target_y < 0 or target_y >= zone.height:
        return MoveResult(accepted=False, x=presence.x, y=presence.y, reason="Out of bounds")

    # Check tile passability
    tile_result = await db.execute(
        select(Tile).where(
            Tile.zone_id == presence.zone_id,
            Tile.x == target_x,
            Tile.y == target_y,
        )
    )
    tile = tile_result.scalar_one_or_none()
    if not tile or not tile.passable:
        terrain = tile.terrain_type if tile else "unknown"
        return MoveResult(accepted=False, x=presence.x, y=presence.y, reason=f"Blocked by {terrain}")

    # Update presence and entity positions
    presence.x = target_x
    presence.y = target_y
    if req.direction:
        presence.facing = req.direction

    entity = await db.get(Entity, presence.entity_id)
    if entity:
        entity.x = target_x
        entity.y = target_y
        if req.direction:
            entity.facing = req.direction

    await db.commit()
    return MoveResult(accepted=True, x=target_x, y=target_y)


@router.get("/zones/{zone_id}/entities", response_model=list[EntityDetail])
async def get_nearby_entities(
    zone_id: str, x: int, y: int, radius: int = 5, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Entity).where(
            Entity.zone_id == zone_id,
            Entity.lifecycle_status == "active",
            Entity.x >= x - radius,
            Entity.x <= x + radius,
            Entity.y >= y - radius,
            Entity.y <= y + radius,
        )
    )
    entities = result.scalars().all()
    return [
        EntityDetail(
            entity_id=e.entity_id,
            entity_type=e.entity_type,
            x=e.x,
            y=e.y,
            facing=e.facing,
            state_blob=json.loads(e.state_blob) if e.state_blob else None,
        )
        for e in entities
    ]


@router.get("/entities/{entity_id}", response_model=EntityDetail)
async def get_entity(entity_id: str, db: AsyncSession = Depends(get_db)):
    entity = await db.get(Entity, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return EntityDetail(
        entity_id=entity.entity_id,
        entity_type=entity.entity_type,
        x=entity.x,
        y=entity.y,
        facing=entity.facing,
        state_blob=json.loads(entity.state_blob) if entity.state_blob else None,
    )
