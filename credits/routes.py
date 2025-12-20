from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from credits.service import CreditService

credits_bp = Blueprint("credits", __name__, url_prefix="/credits")

credit_service = CreditService()


@credits_bp.route("/status", methods=["GET"])
@jwt_required()
def credit_status():
    
    user_id = get_jwt_identity()
    print(user_id)

    credits = credit_service.get_status(user_id)

    return jsonify({
        "success": True,
        "credits": credits
    })


@credits_bp.route("/add", methods=["POST"])
@jwt_required()
def add_credits():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    amount = int(data.get("amount", 0))

    if amount <= 0:
        return jsonify({"error": "Invalid credit amount"}), 400

    credit_service.add_credits(user_id, amount)

    return jsonify({
        "success": True,
        "message": f"{amount} credits added"
    })


@credits_bp.route("/consume", methods=["POST"])
@jwt_required()
def consume_credit():
    user_id = get_jwt_identity()

    success = credit_service.consume_credit(user_id)

    if not success:
        return jsonify({
            "success": False,
            "error": "Credit limit exceeded"
        }), 403

    return jsonify({
        "success": True,
        "message": "1 credit consumed"
    })
