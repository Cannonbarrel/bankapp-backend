import os
import urllib.parse
from flask.cli import load_dotenv
from flask_pymongo import PyMongo

load_dotenv()

# 1. Fetch from env
raw_user = os.getenv("DB_USER")
raw_pass = os.getenv("DB_PASS")

# 2. MANDATORY: Encode them to handle special characters like @, !, etc.
db_user = urllib.parse.quote_plus(raw_user)
db_pass = urllib.parse.quote_plus(raw_pass)

mongo = PyMongo()

def init_db(app):
    # 3. Use the encoded versions
    app.config["MONGO_URI"] = f"mongodb+srv://{db_user}:{db_pass}@cluster0.roeba7n.mongodb.net/my_rest_api_db?retryWrites=true&w=majority"
    mongo.init_app(app)

    # Force a check
    try:
        mongo.db.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect: {e}")