import os
import json
import re
from typing import List, Dict
from openai import OpenAI


class AIService:
    """
    Centralized AI service for meal & recipe generation
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=api_key)

    # ----------------------------------
    # Internal helpers
    # ----------------------------------
    @staticmethod
    def _strip_markdown(text: str) -> str:
        """
        Remove ```json or ``` wrappers and escaped newlines
        """
        text = text.strip()
        text = re.sub(r"^```json|```$", "", text, flags=re.IGNORECASE).strip()
        return text.replace("\\n", "").strip()

    @staticmethod
    def _safe_json_load(text: str):
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON returned by AI: {e}")

    # ----------------------------------
    # Meal Generation
    # ----------------------------------
    def generate_meal_plan(
        self,
        cuisine: str = "any"
    ) -> List[Dict]:

        prompt = f"""
Generate a 7-day meal plan for "{cuisine}"

Return ONLY a valid JSON array.
No markdown. No explanation.

Each item must match:
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
- id must be unique UUID each time
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful meal planning assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        raw = response.choices[0].message.content
        clean = self._strip_markdown(raw)
        parsed = self._safe_json_load(clean)

        if not isinstance(parsed, list):
            raise ValueError("Meal plan is not a list")

        return parsed

    # ----------------------------------
    # Recipe Generation
    # ----------------------------------
    def generate_recipe(self, meal_name: str) -> Dict:
        if not meal_name:
            raise ValueError("meal_name is required")

        prompt = f"""
Generate a detailed recipe for "{meal_name}".

Return ONLY valid JSON.
No markdown. No explanation.

JSON structure:
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
- ingredients & steps must be arrays
- calories & cookingTimeMinutes must be numbers or null
- id must be UUIDs
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional recipe generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )

        raw = response.choices[0].message.content
        clean = self._strip_markdown(raw)
        parsed = self._safe_json_load(clean)

        if not isinstance(parsed, dict):
            raise ValueError("Recipe response is not an object")

        return parsed
