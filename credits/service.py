from credits.models import UserCredits
from database import db

class CreditService:

    def get_status(self, user_id):
        record = UserCredits.query.filter_by(user_id=user_id).first()

        if not record:
            record = UserCredits(user_id=user_id)
            db.session.add(record)
            db.session.commit()

        return {
            "total_credits": record.total_credits,
            "credits_used": record.credits_used,
            "credits_remaining": record.total_credits - record.credits_used
        }

    def can_consume(self, user_id, amount=1):
        record = UserCredits.query.filter_by(user_id=user_id).first()
        if not record:
            return False

        return (record.credits_used + amount) <= record.total_credits

    def consume(self, user_id, amount=1):
        record = UserCredits.query.filter_by(user_id=user_id).first()

        if not record:
            return False

        if (record.credits_used + amount) > record.total_credits:
            return False

        record.credits_used += amount
        db.session.commit()
        return True

    def add_credits(self, user_id, amount):
        record = UserCredits.query.filter_by(user_id=user_id).first()

        if not record:
            record = UserCredits(user_id=user_id, total_credits=amount)
            db.session.add(record)
        else:
            record.total_credits += amount

        db.session.commit()
