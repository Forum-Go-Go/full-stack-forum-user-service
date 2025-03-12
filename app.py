from flask import Flask, jsonify
from database import db
import os
from dotenv import load_dotenv
from flask_cors import CORS

# load env file
load_dotenv()

# get information from .env file
DB_USER = os.getenv("DATABASE_USER")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT")
DB_NAME = os.getenv("DATABASE_NAME")

# construct the database url
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.url_map.strict_slashes = False

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create user table
with app.app_context():
    db.create_all()
    print("---User table created successfully!---")


# root path
@app.route("/")
def index():
    return "Hello from flax"


@app.route("/users", methods=['GET'])
def get_users():
    users = [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'}
    ]
    return jsonify(users)

if __name__ == "__main__":
    app.run(port=5000, debug=True, use_reloader=False)
