from pydantic import BaseModel


class CharacterSummary(BaseModel):
    character_id: str
    character_name: str
    level: int
    archetype: str | None = None
    zone_id: str | None = None


class CreateCharacterRequest(BaseModel):
    account_id: str
    character_name: str
    archetype: str = "warrior"


class CharacterDetail(BaseModel):
    character_id: str
    account_id: str
    character_name: str
    level: int
    experience: int
    world_id: str | None
    zone_id: str | None
    x: int
    y: int
    attributes: "AttributesDetail"
    resources: "ResourcesDetail"
    equipment: list["EquipmentSlot"]
    inventory_count: int


class AttributesDetail(BaseModel):
    strength: int
    agility: int
    intellect: int
    endurance: int
    willpower: int


class ResourcesDetail(BaseModel):
    health_current: int
    health_max: int
    mana_current: int
    mana_max: int
    stamina_current: int
    stamina_max: int


class EquipmentSlot(BaseModel):
    slot_id: str
    item_instance_id: str
    item_name: str | None = None


class EnterWorldResponse(BaseModel):
    character_id: str
    entity_id: str
    zone_id: str
    x: int
    y: int
    zone_width: int
    zone_height: int
    nearby_entities: list[dict]
