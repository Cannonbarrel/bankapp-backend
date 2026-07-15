from typing import List, Dict, Any
from werkzeug.exceptions import BadRequest, NotFound
from Repo import AccountRepository
from Schema import AccountCreate, TransactionRequest

class AccountService:
    def __init__(self, repository: AccountRepository):
        self.repository = repository

    def remove_customer_account(self, account_id: str) -> bool:
        """New method to delete a customer by their username string."""
        if not account_id:
            raise ValueError("Username is required for deletion.")
        return self.repository.delete_account(account_id)

    def create_account(self, data: AccountCreate) -> Dict[str, Any]:
        return self.repository.create(data.userName, data.initial_balance)

    def get_account(self, account_id: str) -> Dict[str, Any]:
        account = self.repository.get_by_id(account_id)
        if not account:
            raise NotFound("Account not found")
        return account

    def get_all_accounts(self):
        # Retrieve all accounts from the database
        return self.repository.get_all_accounts()

    def deposit_funds(self, account_id: str, data: TransactionRequest) -> Dict[str, Any]:
        self.get_account(account_id)
        # Pull account_type directly from the validated schema data!
        updated_account = self.repository.add_transaction(account_id, "deposit", data.amount, data.account_type)
        if not updated_account:
            raise NotFound("Account not found during deposit update")
        return updated_account

    def withdraw_funds(self, account_id: str, data: TransactionRequest) -> Dict[str, Any]:
        account = self.get_account(account_id)

        # Pull account_type directly from the validated schema data
        balance_field = "checking_balance" if data.account_type == "checking" else "savings_balance"
        current_balance = account.get(balance_field, 0.0)

        if current_balance < data.amount:
            raise BadRequest(f"Insufficient funds in {data.account_type} account")

        updated_account = self.repository.add_transaction(account_id, "withdrawal", data.amount, data.account_type)
        if not updated_account:
            raise NotFound("Account not found during withdrawal update")
        return updated_account

    def get_history(self, account_id: str) -> List[Dict[str, Any]]:
        account = self.get_account(account_id)
        return account.get("transactions", [])