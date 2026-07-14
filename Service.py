from typing import List
from werkzeug.exceptions import BadRequest, NotFound
from Repo import ItemRepository
from Schema import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, repository: ItemRepository):
        self.repository = repository

    def add_item(self, item_data: ItemCreate) -> dict:
        return self.repository.create(item_data.model_dump())

    def get_item(self, item_id: str) -> dict:
        item = self.repository.get_by_id(item_id)
        if not item:
            raise NotFound("Item not found")
        return item

    def update_item(self, item_id: str, update_data: ItemUpdate) -> dict:
        self.get_item(item_id)  # Throws 404 if missing

        data_to_update = {k: v for k, v in update_data.model_dump().items() if v is not None}
        if not data_to_update:
            raise BadRequest("No fields to update")

        return self.repository.update(item_id, data_to_update)

    def remove_item(self, item_id: str) -> None:
        self.get_item(item_id)  # Throws 404 if missing
        self.repository.delete(item_id)

    def list_items(self) -> List[dict]:
        return self.repository.get_all()