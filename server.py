import json
from flask import Flask, request, jsonify, Response, send_file
from openai import OpenAI
import re
from datetime import datetime 
import os 
import requests
from dotenv import load_dotenv

app = Flask(__name__)


load_dotenv()  # loads .env automatically

api_key= os.environ["OPENAI_API_KEY"]
if not api_key:
    raise RuntimeError("Please set api_key environment variable.")
client = OpenAI(api_key=api_key)

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

    # Case 1: Already a list → OK
    if isinstance(meals, list):
        return payload

    # Case 2: Must be string
    if not isinstance(meals, str):
        raise ValueError(f"Invalid meals type: {type(meals)}")

    meals = meals.strip()

    if not meals:
        raise ValueError("Meals string is empty")

    # Remove ```json ``` or ``` wrappers
    meals = re.sub(r"^```json|```$", "", meals, flags=re.IGNORECASE).strip()

    # Replace escaped newlines
    meals = meals.replace("\\n", "").strip()

    try:
        parsed_meals = json.loads(meals)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid meals JSON: {e}")

    if not isinstance(parsed_meals, list):
        raise ValueError("Meals JSON is not a list")

    payload["meals"] = parsed_meals
    return payload
@app.route("/", methods=["GET"])
def home():
    file_path = os.path.abspath(
        "../swargamwellnesswebsite/swargamwellness.html"
    )
    return send_file(file_path)

# @app.route("/")
# def health():
#     html = """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8" />
#         <title>AvionMeals API</title>
#         <meta name="viewport" content="width=device-width, initial-scale=1" />

#         <!-- MDBootstrap CSS -->
#         <link
#           href="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/7.2.0/mdb.min.css"
#           rel="stylesheet"
#         />

#         <!-- Font Awesome -->
#         <link
#           href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
#           rel="stylesheet"
#         />
#     </head>

#     <body class="bg-light">

#         <div class="container vh-100 d-flex align-items-center justify-content-center">
#             <div class="card shadow-5-strong" style="max-width: 520px;">
#                 <div class="card-body text-center p-5">

#                     <div class="mb-4">
#                         <i class="fas fa-plane-departure fa-3x text-primary"></i>
#                     </div>

#                     <h2 class="fw-bold mb-2">AvionMeals API</h2>
#                     <p class="text-muted mb-4">
#                         Backend service is running successfully
#                     </p>

#                     <span class="badge badge-success bg-success fs-6 mb-3">
#                         🟢 API STATUS: LIVE
#                     </span>

#                     <hr class="my-4" />

#                     <div class="text-start">
#                         <p class="mb-2">
#                             <i class="fas fa-server me-2 text-secondary"></i>
#                             Environment: <strong>Production</strong>
#                         </p>
#                         <p class="mb-2">
#                             <i class="fas fa-clock me-2 text-secondary"></i>
#                             Server Time: <strong id="time"></strong>
#                         </p>
#                         <p class="mb-0">
#                             <i class="fas fa-cloud me-2 text-secondary"></i>
#                             Platform: <strong>AWS EC2</strong>
#                         </p>
#                     </div>

#                     <div class="mt-4 text-muted small">
#                         © 2025 AvionMeals · All rights reserved
#                     </div>

#                 </div>
#             </div>
#         </div>

#         <!-- MDBootstrap JS -->
#         <script
#           src="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/7.2.0/mdb.min.js">
#         </script>

#         <script>
#             document.getElementById("time").innerText =
#                 new Date().toLocaleString();
#         </script>

#     </body>
#     </html>
#     """
#     return Response(html, mimetype="text/html")
# -----------------------------
# POST /generate-meal
# -----------------------------
@app.route("/generate-meal", methods=["POST"])
def generate_meal():

    data = request.get_json() or {}
    user_id = data.get("user_id", "anonymous")
    cuisine = data.get("cuisine","any")
    print(cuisine)
    prompt = f"""
    Generate a 7-day meal plan for "{cuisine}"
    Return ONLY valid JSON array.
    id should be unique every time
    Format:
    [
      {{
        "id" : "550e8400-e29b-41d4-a716-446655440000",
        "day": "Mon",
        "breakfast": "Oats",
        "lunch": "Dal Rice",
        "dinner": "Roti Sabzi"
      }}
    ]
    """
    print(prompt)

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
        clean_response = normalize_meals(raw_response)["meals"]
        return jsonify(clean_response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate-recipe", methods=["POST"])
def generate_recipe():

    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    meal_name = data.get("meal_name")
    print(meal_name)
    if not meal_name:
        return jsonify({"error": "meal_name is required"}), 400

    prompt = f"""
    Generate a detailed recipe for the dish "{meal_name}".

Respond ONLY with valid JSON.
No markdown.
No explanation.
No extra text.

The JSON MUST match this exact structure:

{{
  "title": "{meal_name}",
  "ingredients": ["string"],
  "steps": ["string"],
  "calories": number or null,
  "cookingTimeMinutes": number or null,
  "dietType": "string or null",
  "id": "string",
  "groceries": [
    {{ "name": "", "quantity": "", "id": "string" }}
  ]
}}

Rules:
- "title" must be the dish name
- "ingredients" must be a list of strings
- "steps" must be a list of strings
- "calories" must be an integer (estimate) or null
- "cookingTimeMinutes" must be an integer or null
- "dietType" must be one of: Vegetarian, Vegan, Eggetarian, Non-Vegetarian, or null
- "id": "uuid unique  every time"
- "groceries": "name": "", "quantity": "", "id": unique uuid string

- Do NOT include "id" (it is generated on the client)

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

        recipe = json.loads(content)
        print(recipe)
        return jsonify(recipe)

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON returned by AI"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

USER_USAGE = {}   # { user_id: count }
FREE_LIMIT = 5
@app.route("/usage-check", methods=["POST"])
def usage_check():

    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    test_mode = data.get("test_mode", False)

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # ✅ Bypass limits during testing
    if test_mode:
        return jsonify({
            "allowed": True,
            "remaining": -1,
            "reason": "test_mode"
        })

    used = USER_USAGE.get(user_id, 0)
    remaining = max(FREE_LIMIT - used, 0)

    return jsonify({
        "allowed": remaining > 0,
        "used": used,
        "remaining": remaining,
        "limit": FREE_LIMIT
    })

# 🔐 Apple App Store credentials (ENV)
APPLE_ISSUER_ID = os.getenv("APPLE_ISSUER_ID")
APPLE_KEY_ID = os.getenv("APPLE_KEY_ID")
APPLE_PRIVATE_KEY = os.getenv("APPLE_PRIVATE_KEY")

# Example in-memory store (replace with DB)
USER_SUBSCRIPTIONS = {}  # { user_id: { is_pro, expiry } }

@app.route("/verify-subscription", methods=["POST"])
def verify_subscription():

    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    transaction_id = data.get("transaction_id")

    if not user_id or not transaction_id:
        return jsonify({"error": "user_id and transaction_id required"}), 400

    try:
        # 🔗 Apple App Store Server API (sandbox or production)
        url = f"https://api.storekit.itunes.apple.com/inApps/v1/transactions/{transaction_id}"

        headers = {
            "Authorization": f"Bearer {generate_apple_jwt()}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return jsonify({"is_pro": False, "reason": "invalid_transaction"}), 403

        result = response.json()

        # ✅ Subscription is valid
        is_pro = result.get("signedTransactionInfo") is not None

        USER_SUBSCRIPTIONS[user_id] = {
            "is_pro": is_pro
        }

        return jsonify({
            "user_id": user_id,
            "is_pro": is_pro
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Simple in-memory event store
# (Replace with DB / analytics tool)
# -----------------------------
EVENTS = []  # list of dicts

@app.route("/track-event", methods=["POST"])
def track_event():

    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    event = data.get("event")
    metadata = data.get("metadata", {})

    if not user_id or not event:
        return jsonify({
            "error": "user_id and event are required"
        }), 400

    event_record = {
        "user_id": user_id,
        "event": event,
        "metadata": metadata,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Store event (replace with DB / Mixpanel / PostHog later)
    EVENTS.append(event_record)

    return jsonify({
        "status": "ok"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)