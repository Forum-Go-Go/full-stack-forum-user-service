from models import db
from sqlalchemy import CheckConstraint

class User(db.Model):
    __tablename__ = 'user'

    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    dateJoined = db.Column(db.DateTime, server_default=db.func.now())
    type = db.Column(db.String(50), nullable=False)  # change to enum type, 0: super admin, 1: admin, 2: user
    profileImageURL = db.Column(db.String(255))

    __table_args__ = (
        CheckConstraint("type IN ('admin', 'user', 'super_admin')", name="check_user_type"),
    )

    def __repr__(self):
        return f"<User {self.email}>"
