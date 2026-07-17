import os
import urllib.parse
from flask_pymongo import PyMongo



#  This safely encodes any special characters (like @ or !) into URL-safe formats
safe_username = urllib.parse.quote_plus(DB_USERNAME)
safe_password = urllib.parse.quote_plus(DB_PASSWORD)

# Initialize the Flask-PyMongo extension instance
mongo = PyMongo()

def init_db(app):
    # We inject the safely encoded strings directly into the URI string
    app.config[
        "MONGO_URI"] = f"mongodb+srv://{safe_username}:{safe_password}@cluster0.roeba7n.mongodb.net/my_rest_api_db?retryWrites=true&w=majority"
    mongo.init_app(app)
