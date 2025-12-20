from database import db
from models import User
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

class UserService:

    @staticmethod
    def get_profile(user_id):
        return User.query.get(user_id)

    @staticmethod
    def update_profile(user_id, data):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return None

        if "phone" in data:
            user.phone = data["phone"]

        if "name" in data:
            user.name = data["name"]

        try:
            db.session.commit()
            return user

        except IntegrityError as e:
            db.session.rollback()

            # 🔴 Phone already exists
            if isinstance(e.orig, UniqueViolation):
                raise ValueError("PHONE_ALREADY_EXISTS")

            raise e

    @staticmethod
    def delete_account(user_id):
        user = User.query.get(user_id)
        if not user:
            return False

        user.is_active = False
        db.session.commit()
        return True

    @staticmethod
    def restore_account(user_id):
        user = User.query.get(user_id)
        if not user:
            return False

        user.is_active = True
        db.session.commit()
        return True
