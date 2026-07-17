import os
import urllib.parse
from flask_pymongo import PyMongo

mongo = PyMongo()

def init_db(app):
    # Retrieve inside the function so it executes after app context is ready
    raw_user = os.getenv("DB_USER")
    raw_pass = os.getenv("DB_PASS")

    # Safety check: if they are None, the app will now report the error
    # instead of crashing with a confusing TypeError
    if raw_user is None or raw_pass is None:
        raise ValueError("DB_USER or DB_PASS environment variables are not set!")

    db_user = urllib.parse.quote_plus(raw_user)
    db_pass = urllib.parse.quote_plus(raw_pass)

    app.config["MONGO_URI"] = f"mongodb+srv://{db_user}:{db_pass}@cluster0.roeba7n.mongodb.net/my_rest_api_db?retryWrites=true&w=majority"
    mongo.init_app(app)