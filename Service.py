# Service.py
from typing import List, Dict, Any
from werkzeug.exceptions import BadRequest, NotFound
from Repo import AccountRepository
from Schema import AccountCreate, TransactionRequest


class AccountService:
    def __init__(self, repository: AccountRepository):
        self.repository = repository

    def create_account(self, data: AccountCreate) -> Dict[str, Any]:
        return self.repository.create(data.userName, data.initial_balance)

    def get_account(self, account_id: str) -> Dict[str, Any]:
        account = self.repository.get_by_id(account_id)
        if not account:
            raise NotFound("Account not found")
        return account

    def deposit_funds(self, account_id: str, data: TransactionRequest) -> Dict[str, Any]:
        # Check if account exists first
        self.get_account(account_id)

        updated_account = self.repository.add_transaction(account_id, "deposit", data.amount)
        if not updated_account:
            raise NotFound("Account not found during deposit update")
        return updated_account

    def withdraw_funds(self, account_id: str, data: TransactionRequest) -> Dict[str, Any]:
        # 1. Verify account exists
        account = self.get_account(account_id)

        # 2. Check balance before allowing withdrawal
        if account["balance"] < data.amount:
            raise BadRequest("Insufficient funds")

        updated_account = self.repository.add_transaction(account_id, "withdrawal", data.amount)
        if not updated_account:
            raise NotFound("Account not found during withdrawal update")
        return updated_account

    def get_history(self, account_id: str) -> List[Dict[str, Any]]:
        account = self.get_account(account_id)
        return account.get("transactions", [])