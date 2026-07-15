from flask import Flask, jsonify, request
from pydantic import ValidationError
from Database import init_db, mongo
from Repo import AccountRepository
from Service import AccountService
from Schema import AccountCreate, TransactionRequest, AccountResponse

app = Flask(__name__)
init_db(app)

account_repository = AccountRepository(mongo)
account_service = AccountService(account_repository)

# 1. Create an Account
@app.route('/accounts', methods=['POST'])
def create_account():
    try:
        data = AccountCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    new_account = account_service.create_account(data)
    return jsonify(AccountResponse(**new_account).model_dump(by_alias=True)), 201

# 2. View Account Details & Balance
@app.route('/accounts/<string:account_id>', methods=['GET'])
def get_account(account_id):
    try:
        account = account_service.get_account(account_id)
        return jsonify(AccountResponse(**account).model_dump(by_alias=True)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route('/accounts', methods=['GET'])
def get_all_accounts():
    try:
        # Check if this matches your service call!
        accounts = account_service.get_all_accounts()
        return jsonify(accounts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# 3. Deposit Money
@app.route('/accounts/<string:account_id>/deposit', methods=['POST'])
def deposit(account_id):
    try:
        data = TransactionRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    try:
        updated_account = account_service.deposit_funds(account_id, data)
        return jsonify(AccountResponse(**updated_account).model_dump(by_alias=True)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 4. Withdraw Money
@app.route('/accounts/<string:account_id>/withdraw', methods=['POST'])
def withdraw(account_id):
    try:
        data = TransactionRequest(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    try:
        updated_account = account_service.withdraw_funds(account_id, data)
        return jsonify(AccountResponse(**updated_account).model_dump(by_alias=True)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
# Add this to your Flask App / Controller file:
@app.route('/accounts/<string:account_id>', methods=['DELETE'])
def delete_account(account_id):
    try:
        # Pass the ID back to the service layer
        success = account_service.remove_customer_account(account_id)
        if success:
            return jsonify({"message": "Account deleted"}), 200
        return jsonify({"error": "Account not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
# 5. View Transaction History
@app.route('/accounts/<string:account_id>/transactions', methods=['GET'])
def get_transaction_history(account_id):
    try:
        history = account_service.get_history(account_id)
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "active", "message": "Banking API is running!"}), 200

if __name__ == "__main__":
    app.run(debug=True)