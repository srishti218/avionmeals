from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from subscription.service import SubscriptionService

subscription_bp = Blueprint("subscription", __name__)


# ----------------------------------
# POST /verify-subscription
# ----------------------------------
@subscription_bp.route("/verify-subscription", methods=["POST"])
@jwt_required()
def verify_subscription():
    data = request.get_json() or {}

    provider = data.get("provider")
    receipt_data = data.get("receipt_data")

    if not provider or not receipt_data:
        return jsonify({
            "error": "provider and receipt_data required"
        }), 400

    valid = SubscriptionService.verify(provider, receipt_data)

    return jsonify({
        "success": valid
    })


# ----------------------------------
# POST /subscription/upgrade
# ----------------------------------
@subscription_bp.route("/subscription/upgrade", methods=["POST"])
@jwt_required()
def upgrade_subscription():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    provider = data.get("provider", "apple")
    duration_days = data.get("duration_days", 30)

    sub = SubscriptionService.upgrade(
        user_id=user_id,
        provider=provider,
        duration_days=duration_days
    )

    return jsonify({
        "success": True,
        "status": sub.status,
        "expiry_date": sub.expiry_date
    })


# ----------------------------------
# GET /subscription/status
# ----------------------------------
@subscription_bp.route("/subscription/status", methods=["GET"])
@jwt_required()
def subscription_status():
    user_id = get_jwt_identity()
    status = SubscriptionService.get_status(user_id)
    return jsonify(status)


# ----------------------------------
# POST /subscription/restore
# ----------------------------------
@subscription_bp.route("/subscription/restore", methods=["POST"])
@jwt_required()
def restore_subscription():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    provider = data.get("provider")
    expiry_date = data.get("expiry_date")

    if not provider or not expiry_date:
        return jsonify({
            "error": "provider and expiry_date required"
        }), 400

    expiry_date = datetime.fromisoformat(expiry_date)

    sub = SubscriptionService.restore(
        user_id=user_id,
        provider=provider,
        expiry_date=expiry_date
    )

    return jsonify({
        "success": True,
        "status": sub.status,
        "expiry_date": sub.expiry_date
    })
