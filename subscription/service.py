from datetime import datetime, timedelta
from database import db
from models import Subscription


class SubscriptionService:
    """
    Handles subscription lifecycle
    """

    @staticmethod
    def get_status(user_id):
        sub = Subscription.query.filter_by(user_id=user_id).first()
        if not sub:
            return {
                "status": "free",
                "expiry_date": None
            }

        is_active = (
            sub.status == "active" and
            sub.expiry_date and
            sub.expiry_date > datetime.utcnow()
        )

        return {
            "status": "active" if is_active else "expired",
            "provider": sub.provider,
            "expiry_date": sub.expiry_date
        }

    @staticmethod
    def upgrade(user_id, provider, duration_days=30):
        expiry = datetime.utcnow() + timedelta(days=duration_days)

        sub = Subscription.query.filter_by(user_id=user_id).first()
        if not sub:
            sub = Subscription(
                user_id=user_id,
                provider=provider,
                status="active",
                expiry_date=expiry
            )
            db.session.add(sub)
        else:
            sub.provider = provider
            sub.status = "active"
            sub.expiry_date = expiry

        db.session.commit()
        return sub

    @staticmethod
    def restore(user_id, provider, expiry_date):
        sub = Subscription.query.filter_by(user_id=user_id).first()

        if not sub:
            sub = Subscription(
                user_id=user_id,
                provider=provider,
                status="active",
                expiry_date=expiry_date
            )
            db.session.add(sub)
        else:
            sub.provider = provider
            sub.status = "active"
            sub.expiry_date = expiry_date

        db.session.commit()
        return sub

    @staticmethod
    def verify(provider, receipt_data):
        """
        Stub for Apple / Google verification
        Replace with real verification logic
        """
        if not receipt_data:
            return False
        return True
