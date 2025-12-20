from database import db


class NotificationService:
    """
    Handles device token registration and updates.
    Tokens are usually for FCM / APNs.
    """

    @staticmethod
    def register_token(user_id, device_token, platform):
        """
        Register a new device token
        """
        record = {
            "user_id": user_id,
            "device_token": device_token,
            "platform": platform
        }
        return record

    @staticmethod
    def update_token(user_id, old_token, new_token):
        """
        Update existing device token
        """
        record = {
            "user_id": user_id,
            "old_token": old_token,
            "new_token": new_token
        }
        return record

    @staticmethod
    def remove_token(user_id, device_token):
        """
        Remove device token
        """
        record = {
            "user_id": user_id,
            "device_token": device_token
        }
        return record
