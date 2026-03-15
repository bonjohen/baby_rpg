from pydantic import BaseModel


class TileDetail(BaseModel):
    x: int
    y: int
    terrain_type: str
    passable: bool
    movement_cost: float


class ZoneDetail(BaseModel):
    zone_id: str
    zone_name: str
    zone_type: str
    width: int
    height: int
    adjacency: dict | None = None
    tiles: list[TileDetail]


class MoveRequest(BaseModel):
    direction: str | None = None  # "north", "south", "east", "west"
    target_x: int | None = None
    target_y: int | None = None


class MoveResult(BaseModel):
    accepted: bool
    x: int
    y: int
    reason: str | None = None


class EntityDetail(BaseModel):
    entity_id: str
    entity_type: str
    x: int
    y: int
    facing: str
    state_blob: dict | None = None
