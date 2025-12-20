from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from meals.service import MealService
from ai.service import AIService
from credits.service import CreditService
import uuid
meals_bp = Blueprint("meals", __name__)

ai_service = AIService()
credit_service = CreditService()

# =================================================
# POST /generate-meal  ✅ (NON-AI ALIAS / WRAPPER)
# =================================================
@meals_bp.route("/generate-meal", methods=["POST"])
@jwt_required(optional=True)
def generate_meal_wrapper():
    data = request.get_json() or {}

    identity = get_jwt_identity()

    user_id = identity if identity is not None else data.get("user_id", str(uuid.uuid4()))
    cuisine = data.get("cuisine", "any")
    success = credit_service.consume(user_id, amount=1)

    if not success:
        return jsonify({
            "error": "Credits exhausted. Please request more credits."
        }), 403
    try:
        # 1️⃣ Generate meal via AI
        meals = ai_service.generate_meal_plan(cuisine)

        # 2️⃣ Save to DB
        MealService.save_meal(
            user_id=user_id,
            meals=meals,
            cuisine=cuisine,
            saved=False
        )

        # 3️⃣ Return clean JSON
        return jsonify(meals)

    except Exception as e:
        return jsonify({
            "error": "Meal generation failed",
            "details": str(e)
        }), 500


# ----------------------------------
# GET /meals/latest
# ----------------------------------
@meals_bp.route("/meals/latest", methods=["GET"])
@jwt_required()
def get_latest_meal():
    user_id = get_jwt_identity()

    meal = MealService.get_latest_meal(user_id)
    if not meal:
        return jsonify({"message": "No meals found"}), 404

    return jsonify({
        "id": meal.id,
        "meals": meal.meals,
        "cuisine": meal.cuisine,
        "created_at": meal.created_at
    })


# ----------------------------------
# GET /meals/history
# ----------------------------------
@meals_bp.route("/meals/history", methods=["GET"])
@jwt_required()
def get_meal_history():
    user_id = get_jwt_identity()
    meals = MealService.get_meal_history(user_id)

    return jsonify([
        {
            "id": m.id,
            "meals": m.meals,
            "cuisine": m.cuisine,
            "created_at": m.created_at,
            "is_saved": m.is_saved
        }
        for m in meals
    ])


# ----------------------------------
# POST /meals/save
# ----------------------------------
@meals_bp.route("/meals/save", methods=["POST"])
@jwt_required()
def save_meal():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    meal_id = data.get("meal_id")     # 👈 NEW
    meals = data.get("meals")
    cuisine = data.get("cuisine")

    if not meals:
        return jsonify({"error": "meals data required"}), 400

    # 🔁 UPDATE if meal_id exists
    if meal_id:
        meal = MealService.update_meal(
            meal_id=meal_id,
            user_id=user_id,
            meals=meals,
            cuisine=cuisine
        )

        if not meal:
            return jsonify({"error": "Meal not found"}), 404

        return jsonify({
            "success": True,
            "meal_id": meal.id,
            "updated": True
        }), 200

    # ➕ CREATE new meal
    meal = MealService.save_meal(
        user_id=user_id,
        meals=meals,
        cuisine=cuisine,
        saved=True
    )

    return jsonify({
        "success": True,
        "meal_id": meal.id,
        "created": True
    }), 201



# ----------------------------------
# DELETE /meals/clear
# ----------------------------------
@meals_bp.route("/meals/clear", methods=["DELETE"])
@jwt_required()
def clear_meals():
    user_id = get_jwt_identity()
    MealService.clear_meals(user_id)

    return jsonify({
        "success": True,
        "message": "All meals cleared"
    })
