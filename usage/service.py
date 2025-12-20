from datetime import datetime, date
from database import db
from models import User


class UsageService:
    """
    Handles per-user usage limits (daily quotas)
    """

    # Example limits (can be subscription-based later)
    FREE_DAILY_LIMIT = 5

    @staticmethod
    def _today():
        return date.today()

    @staticmethod
    def _get_usage_record(user_id):
        """
        Placeholder usage record.
        Replace with DB/Redis-backed implementation.
        """
        # For now, return a simple in-memory style object
        return {
            "used": 0,
            "date": UsageService._today()
        }

    @staticmethod
    def check_usage(user_id):
        usage = UsageService._get_usage_record(user_id)

        allowed = usage["used"] < UsageService.FREE_DAILY_LIMIT

        return {
            "allowed": allowed,
            "used": usage["used"],
            "limit": UsageService.FREE_DAILY_LIMIT
        }

    @staticmethod
    def increment_usage(user_id):
        usage = UsageService._get_usage_record(user_id)
        usage["used"] += 1

        return {
            "used": usage["used"],
            "limit": UsageService.FREE_DAILY_LIMIT
        }

    @staticmethod
    def status(user_id):
        usage = UsageService._get_usage_record(user_id)

        return {
            "used": usage["used"],
            "limit": UsageService.FREE
        }