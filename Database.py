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
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")

    # Debugging: Print to the Railway logs to see what the server actually sees
    print(f"DEBUG: Loaded user: {db_user}")

    if not db_user or not db_pass:
        raise ValueError("Environment variables DB_USER or DB_PASS are not set!")

    encoded_user = urllib.parse.quote_plus(db_user)
    encoded_pass = urllib.parse.quote_plus(db_pass)

    app.config[
        "MONGO_URI"] = f"mongodb+srv://{encoded_user}:{encoded_pass}@cluster0.roeba7n.mongodb.net/my_rest_api_db?retryWrites=true&w=majority"
    mongo.init_app(app)