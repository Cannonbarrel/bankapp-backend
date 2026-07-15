import requests
from abc import ABC, abstractmethod

BASE_URL = "http://127.0.0.1:5000"


class Runner:
    users = []

    @staticmethod
    def initialize_users():
        # Clear out local list first
        Runner.users = []

        # Always add the master admin
        admin = Admin()
        admin.set_username("admin")
        admin.set_password("admin123")
        Runner.users.append(admin)

        # Fetch users dynamically from your backend
        try:
            res = requests.get(f"{BASE_URL}/accounts")
            if res.status_code == 200:
                db_users = res.json()
                for db_user in db_users:
                    customer = Customer()

                    # 1. CLEAN USERNAME EXTRACTION
                    # Grab whichever key your backend is using
                    username_value = db_user.get("username") or db_user.get("userName")
                    customer.set_username(username_value)

                    # 2. CLEAN PASSWORD EXTRACTION
                    customer.set_password(db_user.get("password", "password123"))

                    # 3. CLEAN ID EXTRACTION
                    db_id = db_user.get("id") or db_user.get("_id")

                    # If MongoDB sent back an ObjectId dictionary object, unpack it safely
                    if isinstance(db_id, dict) and "$oid" in db_id:
                        db_id = db_id["$oid"]
                    elif db_id:
                        db_id = str(db_id)

                    # Assign accounts with the cleaned string ID
                    customer.add_account(CheckingAccount(db_id))
                    customer.add_account(SavingsAccount(db_id))

                    Runner.users.append(customer)
            else:
                print("Warning: Backend endpoint GET /accounts returned status", res.status_code)
        except Exception as e:
            print(f"Warning: Offline Mode. Could not connect to API: {e}")

    @staticmethod
    def main():
        Runner.initialize_users()

        print("Welcome to ABC Digital Bank")

        running = True

        while running:
            login_result = Runner.login()

            if login_result == "invalid":
                print("Invalid Credentials")
            elif login_result == "admin":
                Runner.admin_dashboard()
            else:
                Runner.customer_dashboard(login_result)

            answer = input("\nContinue? y/n: ")
            if answer.lower() == "n":
                running = False

    @staticmethod
    def login():
        credentials = input(
            "Enter username and password separated by space: "
        )

        parts = credentials.split()
        if len(parts) != 2:
            return "invalid"

        username = parts[0]
        password = parts[1]

        for user in Runner.users:
            if (user.get_username() == username and
                    user.get_password() == password):
                if user.get_user_type() == "admin":
                    return "admin"
                else:
                    if isinstance(user, Customer):
                        for acct in user.accounts:
                            acct.sync_from_db()
                    return user.get_username()

        return "invalid"

    @staticmethod
    def customer_dashboard(username):
        customer = None
        for user in Runner.users:
            if user.get_username() == username:
                customer = user
                break

        if customer is None:
            print("Customer not found")
            return

        print("\nWelcome customer,", username)

        while True:
            # Sync fresh data from MongoDB for display
            for acct in customer.accounts:
                acct.sync_from_db()

            print("\n1. View Account")
            print("2. Deposit")
            print("3. Withdraw")
            print("4. Transfer")
            print("5. Logout")

            choice = input("Choose option: ")

            if choice == "1":
                for i, account in enumerate(customer.accounts):
                    print(
                        i + 1,
                        "-",
                        type(account).__name__,
                        "Balance: $",
                        f"{account.balance:.2f}"
                    )

            elif choice == "2":
                try:
                    account_num = int(input("Choose account number (1 for Checking, 2 for Savings): "))
                    if account_num < 1 or account_num > len(customer.accounts):
                        print("Invalid account.")
                        continue
                    amount = float(input("Deposit amount: "))
                    customer.accounts[account_num - 1].deposit(amount)
                except ValueError:
                    print("Invalid input.")

            elif choice == "3":
                try:
                    account_num = int(input("Choose account number (1 for Checking, 2 for Savings): "))
                    if account_num < 1 or account_num > len(customer.accounts):
                        print("Invalid account.")
                        continue
                    amount = float(input("Withdraw amount: "))
                    customer.accounts[account_num - 1].withdraw(amount)
                except ValueError:
                    print("Invalid input.")

            elif choice == "4":
                print("\nYour Accounts")
                for i, account in enumerate(customer.accounts):
                    print(i + 1, "-", type(account).__name__)

                try:
                    from_account = int(input("Transfer from account (1 or 2): "))
                    to_account = int(input("Transfer to account (1 or 2): "))

                    if (from_account < 1 or
                            from_account > len(customer.accounts) or
                            to_account < 1 or
                            to_account > len(customer.accounts)):
                        print("Invalid account selection.")
                        continue

                    if from_account == to_account:
                        print("Cannot transfer to the same account.")
                        continue

                    amount = float(input("Transfer amount: "))
                    customer.accounts[from_account - 1].transfer(
                        amount,
                        customer.accounts[to_account - 1]
                    )
                except ValueError:
                    print("Invalid input.")

            elif choice == "5":
                print("Logging out...")
                break
            else:
                print("Invalid option")

    @staticmethod
    def admin_dashboard():
        while True:
            print("\nADMIN MENU")
            print("1. View Customers")
            print("2. Add Customer")
            print("3. Delete Customer")  # New Option!
            print("4. Logout")

            choice = input("Choose option: ")

            if choice == "1":
                print("\n--- Current Customers ---")
                customer_found = False
                for user in Runner.users:
                    if isinstance(user, Customer):
                        print(f"- {user.get_username()}")
                        customer_found = True
                if not customer_found:
                    print("(No customers loaded)")

            elif choice == "2":
                username = input("Username: ")
                password = input("Password: ")

                try:
                    payload = {
                        "userName": username,
                        "password": password,
                        "initial_balance": 0.0
                    }
                    res = requests.post(f"{BASE_URL}/accounts", json=payload)
                    if res.status_code == 201:
                        # Grab ID safely whether the API returns it as "id" or "_id"
                        resp_data = res.json()
                        db_id = resp_data.get("id") or resp_data.get("_id")
                        print(f"Customer '{username}' successfully added to MongoDB!")
                    else:
                        print(f"Error: API returned status {res.status_code}. Fallback to offline ID.")
                        db_id = "temp_id"
                except Exception as e:
                    print(f"Network error trying to contact API: {e}")
                    db_id = "temp_id"

                customer = Customer()
                customer.set_username(username)
                customer.set_password(password)
                customer.add_account(CheckingAccount(db_id))
                customer.add_account(SavingsAccount(db_id))

                Runner.users.append(customer)

            elif choice == "3":  # NEW DELETION LOGIC
                target_username = input("Enter the username of the customer to delete: ")
                target_user = None

                for user in Runner.users:
                    if isinstance(user, Customer) and user.get_username() == target_username:
                        target_user = user
                        break

                if not target_user:
                    print(f"User '{target_username}' not found locally.")
                    continue

                # Find the MongoDB ID from their checking account object
                db_id = target_user.accounts[0].db_id if target_user.accounts else None

                if db_id and db_id != "temp_id":
                    try:
                        # Send DELETE request to your API endpoint
                        res = requests.delete(f"{BASE_URL}/accounts/{db_id}")
                        if res.status_code in [200, 204]:
                            Runner.users.remove(target_user)
                            print(f"Successfully deleted '{target_username}' from MongoDB and local memory!")
                        else:
                            print(f"Backend failed to delete user (Status: {res.status_code}). Reason: {res.text}")
                    except Exception as e:
                        print(f"Failed to connect to API to delete user: {e}")
                else:
                    # Just delete from local array if it wasn't saved in MongoDB
                    Runner.users.remove(target_user)
                    print(f"Deleted '{target_username}' from local runner memory.")

            elif choice == "4":
                break


class User(ABC):
    def __init__(self):
        self.username = ""
        self.password = ""

    def get_username(self):
        return self.username

    def set_username(self, username):
        self.username = username

    def get_password(self):
        return self.password

    def set_password(self, password):
        self.password = password

    @abstractmethod
    def get_user_type(self):
        pass


class Admin(User):
    def get_user_type(self):
        return "admin"


class Customer(User):
    def __init__(self):
        super().__init__()
        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

    def get_user_type(self):
        return "customer"


class AccountOperations(ABC):
    @abstractmethod
    def deposit(self, amount):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass

    @abstractmethod
    def transfer(self, amount, account):
        pass


class Account(ABC):
    counter = 1000

    def __init__(self, db_id=None):
        Account.counter += 1
        self.id = Account.counter
        self.db_id = db_id
        self.balance = 0.0

    def sync_from_db(self):
        if not self.db_id or self.db_id == "temp_id":
            return
        try:
            res = requests.get(f"{BASE_URL}/accounts/{self.db_id}")
            if res.status_code == 200:
                data = res.json()
                field = "checking_balance" if isinstance(self, CheckingAccount) else "savings_balance"
                # Support both naming variations if API uses different key names
                self.balance = data.get(field) or data.get(field.replace("_balance", "")) or 0.0
        except Exception:
            pass


class CheckingAccount(Account, AccountOperations):
    def __init__(self, db_id=None):
        super().__init__(db_id)

    def deposit(self, amount):
        payload = {"amount": amount, "account_type": "checking"}
        try:
            res = requests.post(f"{BASE_URL}/accounts/{self.db_id}/deposit", json=payload)
            if res.status_code == 200:
                data = res.json()
                self.balance = data.get("checking_balance") or data.get("checking") or 0.0
                print(f"Deposit successful! New Balance: ${self.balance:.2f}")
            else:
                print("Deposit failed:", res.text)
        except Exception as e:
            print(f"Error during deposit: {e}")

    def withdraw(self, amount):
        payload = {"amount": amount, "account_type": "checking"}
        try:
            res = requests.post(f"{BASE_URL}/accounts/{self.db_id}/withdraw", json=payload)
            if res.status_code == 200:
                data = res.json()
                self.balance = data.get("checking_balance") or data.get("checking") or 0.0
                print(f"Withdrawal successful! New Balance: ${self.balance:.2f}")
            else:
                print("Withdrawal failed:", res.text)
        except Exception as e:
            print(f"Error during withdrawal: {e}")

    def transfer(self, amount, account):
        payload_withdraw = {"amount": amount, "account_type": "checking"}
        try:
            res_withdraw = requests.post(f"{BASE_URL}/accounts/{self.db_id}/withdraw", json=payload_withdraw)
            if res_withdraw.status_code == 200:
                target_type = "checking" if isinstance(account, CheckingAccount) else "savings"
                payload_deposit = {"amount": amount, "account_type": target_type}
                res_deposit = requests.post(f"{BASE_URL}/accounts/{account.db_id}/deposit", json=payload_deposit)

                if res_deposit.status_code == 200:
                    data_withdraw = res_withdraw.json()
                    data_deposit = res_deposit.json()

                    self.balance = data_withdraw.get("checking_balance") or data_withdraw.get("checking") or 0.0

                    target_field = "checking_balance" if target_type == "checking" else "savings_balance"
                    account.balance = data_deposit.get(target_field) or data_deposit.get(target_type) or 0.0
                    print(f"Transfer successful! Checking: ${self.balance:.2f} | Target: ${account.balance:.2f}")
                else:
                    # Rollback
                    requests.post(f"{BASE_URL}/accounts/{self.db_id}/deposit",
                                  json={"amount": amount, "account_type": "checking"})
                    print("Transfer target deposit failed. Funds rolled back to checking.")
            else:
                print("Transfer withdrawal failed:", res_withdraw.text)
        except Exception as e:
            print(f"Error during transfer: {e}")


class SavingsAccount(Account, AccountOperations):
    def __init__(self, db_id=None):
        super().__init__(db_id)

    def deposit(self, amount):
        payload = {"amount": amount, "account_type": "savings"}
        try:
            res = requests.post(f"{BASE_URL}/accounts/{self.db_id}/deposit", json=payload)
            if res.status_code == 200:
                data = res.json()
                self.balance = data.get("savings_balance") or data.get("savings") or 0.0
                print(f"Deposit successful! New Balance: ${self.balance:.2f}")
            else:
                print("Deposit failed:", res.text)
        except Exception as e:
            print(f"Error during deposit: {e}")

    def withdraw(self, amount):
        payload = {"amount": amount, "account_type": "savings"}
        try:
            res = requests.post(f"{BASE_URL}/accounts/{self.db_id}/withdraw", json=payload)
            if res.status_code == 200:
                data = res.json()
                self.balance = data.get("savings_balance") or data.get("savings") or 0.0
                print(f"Withdrawal successful! New Balance: ${self.balance:.2f}")
            else:
                print("Withdrawal failed:", res.text)
        except Exception as e:
            print(f"Error during withdrawal: {e}")

    def transfer(self, amount, account):
        payload_withdraw = {"amount": amount, "account_type": "savings"}
        try:
            res_withdraw = requests.post(f"{BASE_URL}/accounts/{self.db_id}/withdraw", json=payload_withdraw)
            if res_withdraw.status_code == 200:
                target_type = "checking" if isinstance(account, CheckingAccount) else "savings"
                payload_deposit = {"amount": amount, "account_type": target_type}
                res_deposit = requests.post(f"{BASE_URL}/accounts/{account.db_id}/deposit", json=payload_deposit)

                if res_deposit.status_code == 200:
                    data_withdraw = res_withdraw.json()
                    data_deposit = res_deposit.json()

                    self.balance = data_withdraw.get("savings_balance") or data_withdraw.get("savings") or 0.0

                    target_field = "checking_balance" if target_type == "checking" else "savings_balance"
                    account.balance = data_deposit.get(target_field) or data_deposit.get(target_type) or 0.0
                    print(f"Transfer successful! Savings: ${self.balance:.2f} | Target: ${account.balance:.2f}")
                else:
                    # Rollback
                    requests.post(f"{BASE_URL}/accounts/{self.db_id}/deposit",
                                  json={"amount": amount, "account_type": "savings"})
                    print("Transfer target deposit failed. Funds rolled back to savings.")
            else:
                print("Transfer withdrawal failed:", res_withdraw.text)
        except Exception as e:
            print(f"Error during transfer: {e}")


if __name__ == "__main__":
    Runner.main()