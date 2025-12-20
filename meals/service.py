from datetime import date
from sqlalchemy.exc import SQLAlchemyError

from database import db
from meals.models import Meal


class MealService:
    """
    Business logic layer for Meals
    """

    # 🔽 🔽 🔽 ADD THIS METHOD ONLY 🔽 🔽 🔽
    @staticmethod
    def save_meal(user_id, meals, cuisine=None, saved=False):
        """
        Save AI-generated meal plan (JSON-based)
        """
        try:
            meal = Meal(
                user_id=user_id,
                meals=meals,
                cuisine=cuisine,
                is_saved=saved
            )
            db.session.add(meal)
            db.session.commit()
            return meal
        except SQLAlchemyError as e:
            db.session.rollback()
            raise RuntimeError(str(e))
    # 🔼 🔼 🔼 END ADDITION 🔼 🔼 🔼


    @staticmethod
    def list_meals(user_id):
        return Meal.query.filter_by(user_id=user_id).order_by(Meal.date.desc()).all()

    @staticmethod
    def get_meal(meal_id, user_id):
        return Meal.query.filter_by(id=meal_id, user_id=user_id).first()

    @staticmethod
    def create_meal(user_id, data):
        try:
            meal = Meal(
                user_id=user_id,
                title=data.get("title"),
                calories=data.get("calories"),
                date=data.get("date", date.today()),
                notes=data.get("notes"),
            )
            db.session.add(meal)
            db.session.commit()
            return meal
        except SQLAlchemyError as e:
            db.session.rollback()
            raise RuntimeError(str(e))

    @staticmethod
    def update_meal(meal_id, user_id, meals, cuisine):
        meal = Meal.query.filter_by(
            id=meal_id,
            user_id=user_id
        ).first()

        if not meal:
            return None

        meal.meals = meals
        meal.cuisine = cuisine
        meal.is_saved = True

        db.session.commit()
        return meal
    @staticmethod
    def delete_meal(meal_id, user_id):
        meal = MealService.get_meal(meal_id, user_id)
        if not meal:
            return False

        try:
            db.session.delete(meal)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise RuntimeError(str(e))

    @staticmethod
    def generate_meal(user_id, preferences):
        """
        Placeholder for AI-generated meal.
        AI call should happen in ai/service.py
        """
        meal = Meal(
            user_id=user_id,
            title=f"AI Meal ({preferences})",
            calories=500,
            date=date.today(),
        )
        db.session.add(meal)
        db.session.commit()
        return meal

    @staticmethod
    def get_latest_meal(user_id):
        """
        Return the latest meal entry for a user
        """
        return (
            Meal.query
            .filter_by(user_id=user_id)
            .order_by(Meal.created_at.desc())
            .first()
        )

    @staticmethod
    def get_meal_history(user_id):
        """
        Return all meal entries for a user (latest first)
        """
        return (
            Meal.query
            .filter_by(user_id=user_id)
            .order_by(Meal.created_at.desc())
            .all()
        )

    @staticmethod
    def clear_meals(user_id):
        """
        Delete all meals for a user
        """
        try:
            Meal.query.filter_by(user_id=user_id).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(str(e))

