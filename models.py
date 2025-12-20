from datetime import datetime
from database import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4,
    unique=True,
    nullable=False)
    is_guest = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    is_pro_user = db.Column(
    db.Boolean,
    nullable=False,
    default=False
    )

    free_meal_count = db.Column(
    db.Integer,
    nullable=False,
    default=0
    )

    last_login_at = db.Column(
    db.DateTime(timezone=True),
    nullable=True
    )
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    meals = db.relationship("Meal", backref="user", lazy=True)
    recipes = db.relationship("Recipe", backref="user", lazy=True)
    subscription = db.relationship(
        "Subscription", uselist=False, backref="user"
    )
    


# class Meal(db.Model):
#     __tablename__ = "meals"

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(
#         db.Integer, db.ForeignKey("users.id"), nullable=False
#     )
#     content = db.Column(db.JSON, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)


# class Recipe(db.Model):
#     __tablename__ = "recipes"

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(
#         db.Integer, db.ForeignKey("users.id"), nullable=False
#     )
#     title = db.Column(db.String(255))
#     content = db.Column(db.JSON, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4,
    unique=True,
    nullable=False)
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False
    )
    status = db.Column(db.String(50), default="free")  # free / active / expired
    provider = db.Column(db.String(50))  # apple / google
    expiry_date = db.Column(db.DateTime)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
