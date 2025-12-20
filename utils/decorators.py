from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from subscription.service import SubscriptionService


def jwt_required_optional(fn):
    """
    Allows endpoint to work with or without JWT
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
        except Exception:
            pass
        return fn(*args, **kwargs)
    return wrapper


def subscription_required(fn):
    """
    Restrict endpoint to active subscribers
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()

        status = SubscriptionService.get_status(user_id)
        if status["status"] != "active":
            return jsonify({
                "error": "Active subscription required"
            }), 403

        return fn(*args, **kwargs)
    return wrapper
