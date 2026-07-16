import unittest
from unittest.mock import MagicMock
from werkzeug.exceptions import BadRequest, NotFound
from Service import AccountService
from Schema import TransactionRequest


class TestAccountService(unittest.TestCase):

    def setUp(self):
        # We mock the repository layer so we don't hit the real Atlas DB during tests
        self.mock_repo = MagicMock()
        self.service = AccountService(self.mock_repo)

    def test_withdraw_funds_insufficient_balance_throws_bad_request(self):
        """
        Service layer must prevent a withdrawal and throw a
        BadRequest (400) exception if the account balance is too low.
        """
        # 1. Arrange (Setup mock data)
        account_id = "6a56a9bcb80bfc6bc4b9c80a"
        mock_account = {
            "_id": account_id,
            "userName": "Zachary Cannon",
            "balance": 100.0,  # Balance is only $100
            "transactions": []
        }

        # When get_by_id is called, return our mock account
        self.mock_repo.get_by_id.return_value = mock_account

        # Attempting to withdraw $150 (more than the $100 balance)
        withdraw_request = TransactionRequest(amount=150.0)

        # 2. Act & Assert
        with self.assertRaises(BadRequest) as context:
            self.service.withdraw_funds(account_id, withdraw_request)

        # FIX: Updated to match your actual custom error message in Service.py
        self.assertEqual(str(context.exception), "400 Bad Request: Insufficient funds in checking account")

        # Verify that add_transaction was NEVER called on the database
        self.mock_repo.add_transaction.assert_not_called()

    def test_deposit_funds_successfully_updates(self):
        """
        Service layer successfully deposits funds and calls repo update.
        """
        # 1. Arrange
        account_id = "6a56a9bcb80bfc6bc4b9c80a"
        mock_account = {
            "_id": account_id,
            "userName": "Zachary Cannon",
            "balance": 100.0,
            "transactions": []
        }
        self.mock_repo.get_by_id.return_value = mock_account

        # When deposit is successful, mock the updated account response
        updated_mock_account = {
            "_id": account_id,
            "userName": "Zachary Cannon",
            "balance": 250.0,
            "transactions": [{"type": "deposit", "amount": 150.0}]
        }
        self.mock_repo.add_transaction.return_value = updated_mock_account

        deposit_request = TransactionRequest(amount=150.0)

        # 2. Act
        result = self.service.deposit_funds(account_id, deposit_request)

        # 3. Assert
        self.assertEqual(result["balance"], 250.0)
        # FIX: Added the 'checking' argument to match what your implementation is calling
        self.mock_repo.add_transaction.assert_called_once_with(account_id, "deposit", 150.0, "checking")


if __name__ == "__main__":
    unittest.main()