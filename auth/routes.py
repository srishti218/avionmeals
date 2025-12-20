from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt,
    create_access_token
)
from database import db
from models import User

from auth.utils import (
    hash_password,
    verify_password,
    generate_jwt,
    generate_otp,
    verify_otp
)

auth_bp = Blueprint("auth", __name__)

# -----------------------------
# POST /auth/signup
# -----------------------------
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    name = data.get("name")
    if not password:
        return jsonify({"error": "Password required"}), 400

    if not email and not phone:
        return jsonify({"error": "Email or phone required"}), 400

    if email and User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    if phone and User.query.filter_by(phone=phone).first():
        return jsonify({"error": "Phone already exists"}), 400

    user = User(
        email=email,
        phone=phone,
        name=name,
        password_hash=hash_password(password),
        free_meal_count = 0,
        is_pro_user = False
    )

    db.session.add(user)
    db.session.commit()
    
    return jsonify({"success": True,"user_id": str(user.id)}), 201


# -----------------------------
# POST /auth/login
# -----------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    user = None
    if email:
        user = User.query.filter_by(email=email).first()
    elif phone:
        user = User.query.filter_by(phone=phone).first()

    if not user or not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401
    # ✅ Update last login timestamp (UTC)
    user.last_login_at = datetime.utcnow()
    db.session.commit()
    token = generate_jwt(user.id)

    return jsonify({"success":True,"access_token": token,"user_id": str(user.id)})


# =====================================================
# ✅ NEW APIs START HERE
# =====================================================

# -----------------------------
# POST /auth/logout
# -----------------------------
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    JWT is stateless.
    Client must delete token.
    """
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })


# -----------------------------
# GET /auth/session
# -----------------------------
@auth_bp.route("/session", methods=["GET"])
@jwt_required()
def session():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Invalid session"}), 401

    return jsonify({
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "name": user.name,
        "is_active": user.is_active
    })


# -----------------------------
# POST /auth/forgot-password
# -----------------------------
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}

    email = data.get("email")
    phone = data.get("phone")

    if not email and not phone:
        return jsonify({"error": "Email or phone required"}), 400

    user = None
    if email:
        user = User.query.filter_by(email=email).first()
    elif phone:
        user = User.query.filter_by(phone=phone).first()

    if not user:
        return jsonify({"success": True})  # security: don't reveal user existence

    if phone:
        otp = generate_otp(phone)
        print(f"[RESET OTP] {phone}: {otp}")

    return jsonify({
        "success": True,
        "message": "Password reset OTP sent"
    })


# -----------------------------
# POST /auth/reset-password
# -----------------------------
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}

    phone = data.get("phone")
    otp = data.get("otp")
    new_password = data.get("new_password")

    if not phone or not otp or not new_password:
        return jsonify({
            "error": "phone, otp and new_password required"
        }), 400

    if not verify_otp(phone, otp):
        return jsonify({"error": "Invalid or expired OTP"}), 400

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.password_hash = hash_password(new_password)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Password reset successful"
    })


@auth_bp.route("/guest", methods=["POST"])
def guest_login():
    # Create guest user
    guest_user = User(
        is_guest=True,
        is_pro_user=False,
        free_meal_count=3,  # guest free limit
        last_login_at=datetime.utcnow()
    )

    db.session.add(guest_user)
    db.session.commit()

    # Generate JWT
    token = generate_jwt(guest_user.id)

    return jsonify({
        "access_token": token,
        "user": {
            "id": str(guest_user.id),
            "is_guest": True,
            "free_meal_count": guest_user.free_meal_count
        }
    }), 201