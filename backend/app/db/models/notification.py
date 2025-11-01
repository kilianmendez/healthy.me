from datetime import datetime

def individual_notification_serial(notification) -> dict:
    return {
        "id": str(notification["_id"]),
        "user_id": notification["user_id"],
        "message": notification["message"],
        "read": notification["read"],
        "created_at": notification["created_at"].isoformat(),
    }

def list_notification_serial(notifications) -> list:
    return [individual_notification_serial(notification) for notification in notifications]
