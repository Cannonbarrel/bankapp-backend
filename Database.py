import os
import urllib.parse

from flask.cli import load_dotenv
from flask_pymongo import PyMongo

# This loads the variables from your .env file
load_dotenv()

# Now you can access them like this:
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
# Initialize the Flask-PyMongo extension instance
mongo = PyMongo()

def init_db(app):
    # 3. We inject the safely encoded strings directly into the URI string
    app.config[
        "MONGO_URI"] = f"mongodb+srv://{db_user}:{db_pass}@cluster0.roeba7n.mongodb.net/my_rest_api_db?retryWrites=true&w=majority"
    mongo.init_app(app)