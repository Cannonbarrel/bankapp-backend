import os

from flask import Flask, jsonify, request
from pydantic import ValidationError
from Database import init_db, mongo
from Repo import AccountRepository
from Service import AccountService
from Schema import AccountCreate, TransactionRequest, AccountResponse
from flask_cors import CORS
import jwt
from functools import wraps
from datetime import datetime, timedelta, timezone
app = Flask(__name__)
CORS(app, origins=["https://bankapp-frontend-production.up.railway.app"])
init_db(app)

account_repository = AccountRepository(mongo)
account_service = AccountService(account_repository)

JWT_SECRET = os.urandom(32).hex()

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # 1. Look for 'Authorization: Bearer <token>' in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        # 2. If token is missing, reject immediately
        if not token:
            return jsonify({"error": "Access Forbidden", "reason": "Missing token"}), 403

        try:
            # 3. Decode and verify the token
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

            # 4. Check for Authorization (ROLE_ADMIN only)
            role = payload.get("role")
            if role != "ROLE_ADMIN":
                return jsonify({
                    "error": "Access Forbidden",
                    "reason": "Insufficient permissions (Admin role required)"
                }), 403

        except jwt.ExpiredSignatureError as e:
            return jsonify({"error": "Access Forbidden", "reason": f"Token has expired: {str(e)}"}), 403
        except jwt.InvalidTokenError as e:
            return jsonify({"error": "Access Forbidden", "reason": f"Invalid token: {str(e)}"}), 403

        # If everything passes, let them access the endpoint
        return f(*args, **kwargs)

    return decorated

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

@app.route('/generate-token', methods=['POST'])
def generate_token():
    data = request.json or {}
    username = data.get("username", "Guest")
    password = data.get("password")  # Grab the password from the frontend request
    role = data.get("role", "ROLE_USER")  # Default to regular user

    # SECURITY CHECK: If someone requests ADMIN, they MUST provide the correct password
    if role == "ROLE_ADMIN":
        # Let's enforce a hardcoded admin credential check for your demo
        if username != "admin" or password != "admin123":
            return jsonify({"error": "Unauthorized: Invalid admin credentials."}), 401

    # If they pass the check (or are just a standard ROLE_USER), generate the token
    payload = {
        "sub": "1234567890",
        "username": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return jsonify({"token": token}), 200

@app.route('/admin', methods=['GET'])
@admin_required
def admin_dashboard():
    return jsonify({
        "status": "success",
        "message": "Welcome to the Admin Secure Panel!",
        "system_time": datetime.now(timezone.utc).isoformat()
    }), 200

if __name__ == "__main__":
    app.run(debug=True)