from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime

class AccountRepository:
    def __init__(self, mongo):
        self.mongo = mongo

    def delete_account(self, account_id: str) -> bool:
        try:
            from bson import ObjectId
            mongo_id = ObjectId(account_id)
            result = self.collection.delete_one({"_id": mongo_id})
            return result.deleted_count > 0
        except Exception:  # Catches bad/malformed IDs without needing imports
            return False

    @property
    def collection(self):
        return self.mongo.db.accounts

    def _format_id(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def get_by_id(self, account_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(account_id):
            return None
        doc = self.collection.find_one({"_id": ObjectId(account_id)})
        return self._format_id(doc)

    def get_all_accounts(self):
        accounts_cursor = self.collection.find()
        return list(accounts_cursor)

    def create(self, user_name: str, initial_balance: float) -> Dict[str, Any]:
        account_data = {
            "userName": user_name,
            "checking_balance": initial_balance,
            "savings_balance": 0.0,
            "transactions": []
        }
        result = self.collection.insert_one(account_data)
        account_data["_id"] = str(result.inserted_id)
        return account_data

    def add_transaction(self, account_id: str, tx_type: str, amount: float, account_type: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(account_id):
            return None

        balance_change = amount if tx_type == "deposit" else -amount
        balance_field = "checking_balance" if account_type == "checking" else "savings_balance"

        transaction = {
            "type": f"{tx_type} ({account_type})",
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        }

        self.collection.update_one(
            {"_id": ObjectId(account_id)},
            {
                "$inc": {balance_field: balance_change},
                "$push": {"transactions": transaction}
            }
        )
        return self.get_by_id(account_id)