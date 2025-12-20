from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from notifications.service import NotificationService

notifications_bp = Blueprint("notifications", __name__)


# --------------------------------
# POST /notifications/register
# --------------------------------
@notifications_bp.route("/notifications/register", methods=["POST"])
@jwt_required()
def register_notification():
    data = request.get_json() or {}

    user_id = get_jwt_identity()
    device_token = data.get("device_token")
    platform = data.get("platform")  # ios / android / web

    if not device_token or not platform:
        return jsonify({
            "error": "device_token and platform are required"
        }), 400

    record = NotificationService.register_token(
        user_id=user_id,
        device_token=device_token,
        platform=platform
    )

    return jsonify({
        "success": True,
        "data": record
    }), 201


# --------------------------------
# POST /notifications/update
# --------------------------------
@notifications_bp.route("/notifications/update", methods=["POST"])
@jwt_required()
def update_notification():
    data = request.get_json() or {}

    user_id = get_jwt_identity()
    old_token = data.get("old_token")
    new_token = data.get("new_token")

    if not old_token or not new_token:
        return jsonify({
            "error": "old_token and new_token are required"
        }), 400

    record = NotificationService.update_token(
        user_id=user_id,
        old_token=old_token,
        new_token=new_token
    )

    return jsonify({
        "success": True,
        "data": record
    })


# --------------------------------
# DELETE /notifications/remove
# --------------------------------
@notifications_bp.route("/notifications/remove", methods=["DELETE"])
@jwt_required()
def remove_notification():
    data = request.get_json() or {}

    user_id = get_jwt_identity()
    device_token = data.get("device_token")

    if not device_token:
        return jsonify({
            "error": "device_token is required"
        }), 400

    record = NotificationService.remove_token(
        user_id=user_id,
        device_token=device_token
    )

    return jsonify({
        "success": True,
        "data": record
    })
