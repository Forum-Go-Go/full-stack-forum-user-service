from flask import Blueprint, request, jsonify
from models import db  # Use the shared db instance
from models.user import User
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import json
import random
# import redis
# import pika
import boto3
import os

AWS_S3_BUCKET = 'fa-forum-user-profile-bucket'
AWS_REGION='us-east-1'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

user_bp = Blueprint("user_bp", __name__, url_prefix='/users')

# Redis used ofr storing verification code
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# RabbitMQ connection
# rabbitmq_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = rabbitmq_connection.channel()
# channel.queue_declare(queue='email_queue')

# generate 6-digit random code
# def generate_verification_code(length=6):
#     return ''.join(random.choices("0123456789", k=length))

# user register, without email verification
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
            type=data["type"],
            verified=False  # just register without email verification
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
                "dateJoined": new_user.dateJoined.strftime("%Y-%m-%d"),
                "type": new_user.type,
                "verified": new_user.verified
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

# @user_bp.route("/search", methods=["GET"])
# def search_user_by_email():
#     """
#     Fetch a user's details based on an email query parameter.
#     Expected request: GET /users/search?email=user@example.com
#     Returns full user details including the hashed password.
#     """
#     email = request.args.get("email")
#     if not email:
#         return jsonify({"error": "Email parameter is required."}), 400

#     # Retrieve the user from the database by email
#     user = User.query.filter_by(email=email).first()
#     if not user:
#         return jsonify({"error": "User not found."}), 404

    # Prepare a response that includes the hashed password for internal use.
    # Note: Exposing the hashed password publicly is not recommended.
    # user_data = {
    #     "id": user.userId,
    #     "firstName": user.firstName,
    #     "lastName": user.lastName,
    #     "email": user.email,
    #     "hashedPassword": user.password,  # Assuming the model field is named 'password'
    #     "dateJoined": user.dateJoined.strftime("%Y-%m-%d") if user.dateJoined else None,
    #     "profileImageURL": user.profileImageURL,
    #     "type": user.type
    # }
    # return jsonify(user_data), 200

# request email verification: send code to user's email
# @user_bp.route("/verify_email/request", methods=["POST"])
# def request_verification():
#     data = request.get_json()

#     if not data or "email" not in data:
#         return jsonify({"error": "Email is required"}), 400
    
#     user = User.query.filter_by(email=data["email"]).first()
#     if not user:
#         return jsonify({"error": "User not found"}), 404
    
#     # send verification code
#     if "code" not in data:
#         if user.verified:
#             return jsonify({"message": "Email is alread verified"}), 200
    
#         # generate and store verification code in Redis, 3 - hour expiration 
#         verification_code = generate_verification_code()
#         redis_client.setex(f"email_verif:{data['email']}", 10800, verification_code)  # key name: email_verif

#         # send message to RabbitMQ
#         email_payload = {
#             "email": data["email"],
#             "code": verification_code
#         }
#         channel.basic_publish(exchange='', routing_key='email_queue', body=json.dumps(email_payload))

        # debug: check the generated code
        # print(f"Generated verification code for {data['email']}: {verification_code}")

        # return jsonify({"message": "Verfication email sent"}), 200

# verfiy email code
# @user_bp.route("/verify_email", methods=["POST"])
# def verify_email():
#     data = request.get_json()

#     if not data or "email" not in data or "code" not in data:
#         return jsonify({"error": "Invalid request"}), 400

#     stored_code = redis_client.get(f"email_verif:{data['email']}")
#     if not stored_code:
#         return jsonify({"error": "Verification code expired or invalid"}), 400
    
#     if stored_code == data['code']:
#         user = User.query.filter_by(email=data["email"]).first()
#         if user:
#             user.verified = True
#             db.session.commit()

    #         redis_client.delete(f"email_verif:{data['email']}")  # remove code from Redis after verification
            
    #         return jsonify({
    #             "message": "Email verified successfully!",
    #             "user": {
    #                 "id": user.userId,
    #                 "email": user.email,
    #                 "verified": user.verified
    #             }
    #         }), 200
    # return jsonify({"error": "Invalid verification code"}), 400

# # user login
# @user_bp.route("/login", methods=["POST"])
# def login():
#     return jsonify({"message": "Login endpoint working"}), 200
#     # data = request.get_json()
#     # user = User.query.filter_by(email=data.get("email")).first()
    

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
        }), 200
    
    elif request.method == "PUT":
        # First, check if the request contains both form data and files
        data = request.form.to_dict() if "profileImage" in request.files else request.get_json()

        if not data:
            return jsonify({"error": "Invalid request, JSON data or file required"}), 400

        # Check if a profile image is included in the request
        if "profileImage" in request.files:
            image = request.files["profileImage"]

            if image.filename == "":
                return jsonify({"error": "No selected file"}), 400

            filename = secure_filename(image.filename)
            s3_key = f"profile_images/user_{user_id}/{filename}"

            try:
                # Upload image to AWS S3
                s3_client.upload_fileobj(
                image,
                AWS_S3_BUCKET,
                s3_key,
                ExtraArgs={"ContentType": image.content_type},
            )

                # Store the S3 URL in the user profile
                user.profileImageURL = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
            except Exception as e:
                return jsonify({"error": f"Image upload failed: {str(e)}"}), 500


            # try:
            #     # Upload image to AWS S3
            #     s3_client.upload_fileobj(
            #         image,
            #         AWS_S3_BUCKET,
            #         s3_key,
            #         ExtraArgs={"ACL": "public-read", "ContentType": image.content_type},
            #     )

            #     # Store the S3 URL in the user profile
            #     user.profileImageURL = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
            # except Exception as e:
            #     return jsonify({"error": f"Image upload failed: {str(e)}"}), 500

        # Update user details (email, etc.) if provided
        if "email" in data:
            user.email = data["email"]
        
        # Commit changes to the database
        db.session.commit()

        # Return the updated user profile
        return jsonify({
            "message": "Profile updated successfully",
            "user": {
                "id": user.userId,
                "email": user.email,
                "profileImageURL": user.profileImageURL,
                "type": user.type
            }
        }), 200
