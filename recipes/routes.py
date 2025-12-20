from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from recipes.service import RecipeService
from credits.service import CreditService
from ai.service import AIService

recipes_bp = Blueprint("recipes", __name__)

ai_service = AIService()
credit_service = CreditService()

# =================================================
# POST /generate-recipe  ✅ (NON-AI ALIAS / WRAPPER)
# =================================================
@recipes_bp.route("/generate-recipe", methods=["POST"])
@jwt_required(optional=True)
def generate_recipe_wrapper():
    data = request.get_json() or {}

    user_id = get_jwt_identity() or data.get("user_id", "anonymous")
    meal_name = data.get("meal_name")
    success = credit_service.consume(user_id, amount=1)

    if not success:
        return jsonify({
            "error": "Credits exhausted. Please request more credits."
        }), 403
    if not meal_name:
        return jsonify({"error": "meal_name is required"}), 400

    try:
        # 1️⃣ Generate recipe via AI
        recipe_json = ai_service.generate_recipe(meal_name)

        # 2️⃣ Save to DB
        RecipeService.save_recipe(
            user_id=user_id,
            title=recipe_json.get("title", meal_name),
            content=recipe_json,
            saved=False
        )

        # 3️⃣ Return clean JSON
        return jsonify(recipe_json)

    except Exception as e:
        return jsonify({
            "error": "Recipe generation failed",
            "details": str(e)
        }), 500


# ----------------------------------
# GET /recipe/latest
# ----------------------------------
@recipes_bp.route("/recipe/latest", methods=["GET"])
@jwt_required()
def get_latest_recipe():
    user_id = get_jwt_identity()

    recipe = RecipeService.get_latest_recipe(user_id)
    if not recipe:
        return jsonify({"message": "No recipe found"}), 404

    return jsonify({
        "id": recipe.id,
        "title": recipe.title,
        "content": recipe.content,
        "created_at": recipe.created_at
    })


# ----------------------------------
# POST /recipe/save
# ----------------------------------
@recipes_bp.route("/recipe/save", methods=["POST"])
@jwt_required()
def save_recipe():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({
            "error": "title and content are required"
        }), 400

    recipe = RecipeService.save_recipe(
        user_id=user_id,
        title=title,
        content=content,
        saved=True
    )

    return jsonify({
        "success": True,
        "recipe_id": recipe.id
    }), 201


# ----------------------------------
# GET /recipe/<id>
# ----------------------------------
@recipes_bp.route("/recipe/<int:recipe_id>", methods=["GET"])
@jwt_required()
def get_recipe_by_id(recipe_id):
    user_id = get_jwt_identity()

    recipe = RecipeService.get_recipe_by_id(
        user_id=user_id,
        recipe_id=recipe_id
    )

    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404

    return jsonify({
        "id": recipe.id,
        "title": recipe.title,
        "content": recipe.content,
        "created_at": recipe.created_at
    })
