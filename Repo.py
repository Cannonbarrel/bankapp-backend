from typing import List, Optional, Dict, Any
from bson import ObjectId

class ItemRepository:
    def __init__(self, mongo_db):
        self.collection = mongo_db.items

    def _format_id(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(item_id):
            return None
        doc = self.collection.find_one({"_id": ObjectId(item_id)})
        return self._format_id(doc)

    def get_all(self) -> List[Dict[str, Any]]:
        cursor = self.collection.find({})
        return [self._format_id(doc) for doc in cursor]

    def create(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        result = self.collection.insert_one(item_data)
        item_data["_id"] = str(result.inserted_id)
        return item_data

    def update(self, item_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(item_id):
            return None
        self.collection.update_one({"_id": ObjectId(item_id)}, {"$set": update_data})
        return self.get_by_id(item_id)

    def delete(self, item_id: str) -> bool:
        if not ObjectId.is_valid(item_id):
            return False
        result = self.collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count > 0