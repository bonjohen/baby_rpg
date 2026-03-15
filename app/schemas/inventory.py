from pydantic import BaseModel


class ItemInstanceDetail(BaseModel):
    item_instance_id: str
    item_def_id: str
    item_name: str
    item_category: str
    quantity: int
    owner_type: str
    owner_id: str


class AddItemRequest(BaseModel):
    item_def_id: str
    quantity: int = 1


class DropItemRequest(BaseModel):
    quantity: int | None = None  # None means drop entire stack


class EquipRequest(BaseModel):
    item_instance_id: str
    slot_id: str


class EquipmentDetail(BaseModel):
    slot_id: str
    item_instance_id: str
    item_name: str
    item_category: str
    stats: dict | None = None
