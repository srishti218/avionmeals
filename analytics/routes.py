from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from analytics.service import AnalyticsService

analytics_bp = Blueprint("analytics", __name__)


# --------------------------------
# POST /track-event
# --------------------------------
@analytics_bp.route("/track-event", methods=["POST"])
@jwt_required(optional=True)
def track_event():
    data = request.get_json() or {}

    user_id = get_jwt_identity() or data.get("user_id", "anonymous")
    event_name = data.get("event")
    metadata = data.get("metadata", {})

    if not event_name:
        return jsonify({"error": "event is required"}), 400

    record = AnalyticsService.track_event(
        user_id=user_id,
        event_name=event_name,
        metadata=metadata
    )

    return jsonify({"success": True, "data": record})


# --------------------------------
# POST /track-session
# --------------------------------
@analytics_bp.route("/track-session", methods=["POST"])
@jwt_required(optional=True)
def track_session():
    data = request.get_json() or {}

    user_id = get_jwt_identity() or data.get("user_id", "anonymous")
    session_id = data.get("session_id")
    metadata = data.get("metadata", {})

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    record = AnalyticsService.track_session(
        user_id=user_id,
        session_id=session_id,
        metadata=metadata
    )

    return jsonify({"success": True, "data": record})


# --------------------------------
# POST /track-error
# --------------------------------
@analytics_bp.route("/track-error", methods=["POST"])
@jwt_required(optional=True)
def track_error():
    data = request.get_json() or {}

    user_id = get_jwt_identity() or data.get("user_id", "anonymous")
    error_message = data.get("error")
    stack_trace = data.get("stack_trace")

    if not error_message:
        return jsonify({"error": "error is required"}), 400

    record = AnalyticsService.track_error(
        user_id=user_id,
        error_message=error_message,
        stack_trace=stack_trace
    )

    return jsonify({"success": True, "data": record})
