import os
import json
import re
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from credits.service import CreditService
from openai import OpenAI

from database import db
from meals.models import Meal
from recipes.models import Recipe

ai_bp = Blueprint("ai", __name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ------------------------------------
# Utility: Normalize Meals JSON
# ------------------------------------
def normalize_meals(payload: dict) -> dict:
    """
    Normalize 'meals' into a proper JSON list.
    Handles:
    - list
    - stringified JSON
    - markdown wrapped JSON
    - escaped newlines
    """

    meals = payload.get("meals")

    # Case 1: Already a list
    if isinstance(meals, list):
        return payload

    # Case 2: Must be string
    if not isinstance(meals, str):
        raise ValueError(f"Invalid meals type: {type(meals)}")

    meals = meals.strip()
    if not meals:
        raise ValueError("Meals string is empty")

    # Remove ```json or ``` wrappers
    meals = re.sub(r"^```json|```$", "", meals, flags=re.IGNORECASE).strip()

    # Remove escaped newlines
    meals = meals.replace("\\n", "").strip()

    try:
        parsed_meals = json.loads(meals)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid meals JSON: {e}")

    if not isinstance(parsed_meals, list):
        raise ValueError("Meals JSON is not a list")

    payload["meals"] = parsed_meals
    return payload


# ------------------------------------
# POST /ai/generate-meal
# ------------------------------------
@ai_bp.route("/generate-meal", methods=["POST"])
@jwt_required(optional=True)
def generate_meal():
    data = request.get_json() or {}
    identity = get_jwt_identity()
    
    user_id = identity if identity is not None else data.get("user_id", str(uuid.uuid4()))
    success = CreditService.consume(user_id, amount=1)

    if not success:
        return jsonify({
            "error": "Credits exhausted. Please request more credits."
        }), 403
    cuisine = data.get("cuisine", "any")

    prompt = f"""
Generate a 7-day meal plan for "{cuisine}"

Return ONLY a valid JSON array.
No markdown.
No explanation.

Each item must follow this format:
[
  {{
    "id": "uuid",
    "day": "Mon",
    "breakfast": "Oats",
    "lunch": "Dal Rice",
    "dinner": "Roti Sabzi"
  }}
]

Rules:
- id must be a unique UUID every time
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful meal planning assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content

        raw_response = {
            "user_id": user_id,
            "meals": content
        }

        clean_meals = normalize_meals(raw_response)["meals"]

        # Store in DB
        meal = Meal(user_id=user_id, content=clean_meals)
        db.session.add(meal)
        db.session.commit()

        return jsonify(clean_meals)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------
# POST /ai/generate-recipe
# ------------------------------------
@ai_bp.route("/generate-recipe", methods=["POST"])
@jwt_required(optional=True)
def generate_recipe():
    data = request.get_json(silent=True) or {}

    user_id = get_jwt_identity() or data.get("user_id", "anonymous")
    meal_name = data.get("meal_name")
    success = CreditService.consume(user_id, amount=1)

    if not success:
        return jsonify({
            "error": "Credits exhausted. Please request more credits."
        }), 403
    if not meal_name:
        return jsonify({"error": "meal_name is required"}), 400

    prompt = f"""
Generate a detailed recipe for the dish "{meal_name}".

Respond ONLY with valid JSON.
No markdown.
No explanation.
No extra text.

JSON structure MUST be:

{{
  "title": "{meal_name}",
  "ingredients": ["string"],
  "steps": ["string"],
  "calories": number or null,
  "cookingTimeMinutes": number or null,
  "dietType": "Vegetarian | Vegan | Eggetarian | Non-Vegetarian | null",
  "id": "uuid",
  "groceries": [
    {{ "name": "", "quantity": "", "id": "uuid" }}
  ]
}}

Rules:
- ingredients and steps must be arrays
- calories & cookingTimeMinutes must be integers or null
- id must be unique UUIDs
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional recipe generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )

        content = response.choices[0].message.content.strip()
        recipe_json = json.loads(content)

        # Store in DB
        recipe = Recipe(
            user_id=user_id,
            title=meal_name,
            content=recipe_json
        )
        db.session.add(recipe)
        db.session.commit()

        return jsonify(recipe_json)

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON returned by AI"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
