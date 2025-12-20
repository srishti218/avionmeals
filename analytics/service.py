from datetime import datetime
from database import db


class AnalyticsService:
    """
    Handles analytics persistence and business logic
    """

    @staticmethod
    def track_event(user_id, event_name, metadata=None):
        record = {
            "type": "event",
            "event": event_name,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        return record

    @staticmethod
    def track_session(user_id, session_id, metadata=None):
        record = {
            "type": "session",
            "session_id": session_id,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        return record

    @staticmethod
    def track_error(user_id, error_message, stack_trace=None):
        record = {
            "type": "error",
            "error": error_message,
            "stack_trace": stack_trace,
            "timestamp": datetime.utcnow().isoformat()
        }
        return record
