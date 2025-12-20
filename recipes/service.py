from database import db
from recipes.models import Recipe


class RecipeService:

    @staticmethod
    def save_recipe(user_id, title, content, saved=True):
        recipe = Recipe(
            user_id=user_id,
            title=title,
            content=content,
            is_saved=saved
        )
        db.session.add(recipe)
        db.session.commit()
        return recipe

    @staticmethod
    def get_latest_recipe(user_id):
        return (
            Recipe.query
            .filter_by(user_id=user_id)
            .order_by(Recipe.created_at.desc())
            .first()
        )

    @staticmethod
    def get_recipe_by_id(user_id, recipe_id):
        return (
            Recipe.query
            .filter_by(id=recipe_id, user_id=user_id)
            .first()
        )
