from abc import ABC, abstractmethod

class Runner:

    users = []

    @staticmethod
    def initialize_users():

        admin = Admin()
        admin.set_username("admin")
        admin.set_password("admin123")

        customer1 = Customer()
        customer1.set_username("cannon")
        customer1.set_password("cannon123")
        customer1.add_account(CheckingAccount())
        customer1.add_account(SavingsAccount())

        customer2 = Customer()
        customer2.set_username("bannon")
        customer2.set_password("bannon123")
        customer2.add_account(CheckingAccount())
        customer2.add_account(SavingsAccount())

        customer3 = Customer()
        customer3.set_username("shannon")
        customer3.set_password("shannon123")
        customer3.add_account(CheckingAccount())
        customer3.add_account(SavingsAccount())

        Runner.users.append(admin)
        Runner.users.append(customer1)
        Runner.users.append(customer2)
        Runner.users.append(customer3)

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
                        account.balance
                    )

            elif choice == "2":

                account_num = int(input("Choose account number: "))

                if account_num < 1 or account_num > len(customer.accounts):
                    print("Invalid account.")
                    continue

                amount = float(input("Deposit amount: "))

                customer.accounts[account_num - 1].deposit(amount)

            elif choice == "3":

                account_num = int(input("Choose account number, 1 for checking 2 for savings: "))

                if account_num < 1 or account_num > len(customer.accounts):
                    print("Invalid account.")
                    continue

                amount = float(input("Withdraw amount: "))

                customer.accounts[account_num - 1].withdraw(amount)

            elif choice == "4":

                print("\nYour Accounts")

                for i, account in enumerate(customer.accounts):
                    print(i + 1, "-", type(account).__name__)

                from_account = int(input("Transfer from account: "))
                to_account = int(input("Transfer to account: "))

                if (from_account < 1 or
                        from_account > len(customer.accounts) or
                        to_account < 1 or
                        to_account > len(customer.accounts)):
                    print("Invalid account.")
                    continue

                if from_account == to_account:
                    print("Cannot transfer to the same account.")
                    continue

                amount = float(input("Transfer amount: "))

                customer.accounts[from_account - 1].transfer(
                    amount,
                    customer.accounts[to_account - 1]
                )

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
            print("3. Logout")

            choice = input("Choose option: ")

            if choice == "1":


                for user in Runner.users:


                    if isinstance(user, Customer):

                        print(
                            user.get_username()
                        )

            elif choice == "2":


                username = input("Username: ")
                password = input("Password: ")


                customer = Customer()

                customer.set_username(username)
                customer.set_password(password)

                customer.add_account(
                    CheckingAccount()
                )


                Runner.users.append(customer)


                print("Customer added")



            elif choice == "3":

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

    def __init__(self):

        Account.counter += 1

        self.id = Account.counter

        self.balance = 0

class CheckingAccount(Account, AccountOperations):


    def deposit(self, amount):

        self.balance += amount

        print("Deposit successful")

    def withdraw(self, amount):

        if amount <= self.balance:

            self.balance -= amount

            print("Withdrawal successful")

        else:

            print("Insufficient funds")

    def transfer(self, amount, account):

        if amount <= self.balance:

            self.balance -= amount

            account.deposit(amount)

            print("Transfer successful")

        else:

            print("Insufficient funds")

class SavingsAccount(Account, AccountOperations):


    def deposit(self, amount):

        self.balance += amount

        print("Deposit successful")

    def withdraw(self, amount):

        if amount <= self.balance:

            self.balance -= amount

            print("Withdrawal successful")

        else:

            print("Insufficient funds")

    def transfer(self, amount, account):

        if amount <= self.balance:

            self.balance -= amount

            account.deposit(amount)

            print("Transfer successful")

        else:

            print("Insufficient funds")
Runner.main()