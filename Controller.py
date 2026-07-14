from flask import Flask, jsonify, request
from pydantic import ValidationError
from Database import init_db, mongo
from Repo import AccountRepository
from Schema import AccountCreate, TransactionRequest, AccountResponse

app = Flask(__name__)
init_db(app)

account_repository = AccountRepository(mongo)


# 1. Create an Account
@app.route('/accounts', methods=['POST'])
def create_account():
    try:
        data = AccountCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    new_account = account_repository.create(data.userName, data.initial_balance)
    return jsonify(AccountResponse(**new_account).model_dump(by_alias=True)), 201


# 2. View Account Details & Balance
@app.route('/accounts/<string:account_id>', methods=['GET'])
def get_account(account_id):
    account = account_repository.get_by_id(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(AccountResponse(**account).model_dump(by_alias=True)), 200


# 3. Deposit Money
@app.route('/accounts/<string:account_id>/deposit', methods=['POST'])
def deposit(account_id):
    try:
        data = TransactionRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    updated_account = account_repository.add_transaction(account_id, "deposit", data.amount)
    if not updated_account:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(AccountResponse(**updated_account).model_dump(by_alias=True)), 200


# 4. Withdraw Money
@app.route('/accounts/<string:account_id>/withdraw', methods=['POST'])
def withdraw(account_id):
    try:
        data = TransactionRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    # Get current account to check funds
    account = account_repository.get_by_id(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404

    if account["balance"] < data.amount:
        return jsonify({"error": "Insufficient funds"}), 400

    updated_account = account_repository.add_transaction(account_id, "withdrawal", data.amount)
    return jsonify(AccountResponse(**updated_account).model_dump(by_alias=True)), 200


# 5. View Transaction History (Returns just the history array)
@app.route('/accounts/<string:account_id>/transactions', methods=['GET'])
def get_transaction_history(account_id):
    account = account_repository.get_by_id(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(account.get("transactions", [])), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "active", "message": "Banking API is running!"}), 200
if __name__ == "__main__":
    app.run(debug=True)