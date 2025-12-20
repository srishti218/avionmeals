from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from user.service import UserService

user_bp = Blueprint("user", __name__)


# ----------------------------------
# GET /user/profile
# ----------------------------------
@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = UserService.get_profile(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "is_active": user.is_active,
        "created_at": user.created_at
    })


# ----------------------------------
# PUT /user/profile
# ----------------------------------
@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    try:
        user = UserService.update_profile(user_id, data)

        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Profile updated"
        })

    except ValueError as e:
        if str(e) == "PHONE_ALREADY_EXISTS":
            return jsonify({
                "success": False,
                "error": "Phone number already exists"
            }), 409



# ----------------------------------
# DELETE /user/account
# ----------------------------------
@user_bp.route("/account", methods=["DELETE"])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()

    success = UserService.delete_account(user_id)
    if not success:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "success": True,
        "message": "Account deactivated"
    })


# ----------------------------------
# POST /user/restore
# ----------------------------------
@user_bp.route("/restore", methods=["POST"])
@jwt_required()
def restore_account():
    user_id = get_jwt_identity()

    success = UserService.restore_account(user_id)
    if not success:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "success": True,
        "message": "Account restored"
    })
