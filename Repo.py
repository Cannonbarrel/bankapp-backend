from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime


class AccountRepository:
    def __init__(self, mongo):
        self.mongo = mongo

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

    def create(self, user_name: str, initial_balance: float) -> Dict[str, Any]:
        account_data = {
            "userName": user_name,
            "balance": initial_balance,
            "transactions": []
        }
        result = self.collection.insert_one(account_data)
        account_data["_id"] = str(result.inserted_id)
        return account_data

    def add_transaction(self, account_id: str, tx_type: str, amount: float) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(account_id):
            return None

        # Calculate balance change (+ for deposit, - for withdrawal)
        balance_change = amount if tx_type == "deposit" else -amount

        transaction = {
            "type": tx_type,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        }

        # Update the balance and append to the transaction history array in one go
        self.collection.update_one(
            {"_id": ObjectId(account_id)},
            {
                "$inc": {"balance": balance_change},
                "$push": {"transactions": transaction}
            }
        )
        return self.get_by_id(account_id)