from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from usage.service import UsageService

usage_bp = Blueprint("usage", __name__)


# ----------------------------------
# POST /usage-check
# ----------------------------------
@usage_bp.route("/usage-check", methods=["POST"])
@jwt_required()
def usage_check():
    user_id = get_jwt_identity()
    result = UsageService.check_usage(user_id)
    return jsonify(result)


# ----------------------------------
# POST /usage-increment
# ----------------------------------
@usage_bp.route("/usage-increment", methods=["POST"])
@jwt_required()
def usage_increment():
    user_id = get_jwt_identity()
    result = UsageService.increment_usage(user_id)
    return jsonify(result)


# ----------------------------------
# GET /usage/status
# ----------------------------------
@usage_bp.route("/usage/status", methods=["GET"])
@jwt_required()
def usage_status():
    user_id = get_jwt_identity()
    result = UsageService.status(user_id)
    return jsonify(result)
