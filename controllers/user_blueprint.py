from flask import Blueprint, request, jsonify
from models import db  # Use the shared db instance
from models.user import User
from werkzeug.security import generate_password_hash

user_bp = Blueprint("user_bp", __name__, url_prefix='/users')

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request, JSON data required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400

    try:
        hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")
        new_user = User(
            firstName=data["firstName"],
            lastName=data["lastName"],
            email=data["email"],
            password=hashed_password,
            type=data["type"]
        )

        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": new_user.userId,
                "firstName": new_user.firstName,
                "lastName": new_user.lastName,
                "email": new_user.email,
                "dateJoined": new_user.dateJoined,
                "type": new_user.type
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


# user login
@user_bp.route("/login", methods=["POST"])
def login():
    return jsonify({"message": "Login endpoint working"}), 200
    # data = request.get_json()
    # user = User.query.filter_by(email=data.get("email")).first()
    

# get/edit user profile
@user_bp.route("/<int:user_id>/profile", methods=["GET", "PUT"])
def get_user_profile(user_id):
    
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if request.method == "GET":
      return jsonify({
              "user": {
                  "id": user.userId,
                  "firstName": user.firstName,
                  "lastName": user.lastName,
                  "email": user.email,
                  "dateJoined": user.dateJoined.strftime("%Y-%m-%d"),
                  "profileImageURL": user.profileImageURL,
                  "type": user.type,
                  "topPosts": [],
                  "drafts": [],
                  "viewHistory": [],
              }
          }), 201
    
    elif request.method == "PUT":
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid request, JSON data required"}), 400

        # email verifcation? should we add new col of verfiy?
        if "email" in data:
            user.email = data["email"]
        
        if "profileImageURL" in data:
            user.profileImageURL = data["profileImageURL"]
        
        db.session.commit()

        return jsonify({
            "message": "Profile updated successfully",
            "user": {
                "id": user.userId,
                "email": user.email,
                "profileImageURL": user.profileImageURL,
                "type": user.type
            }
        }), 200