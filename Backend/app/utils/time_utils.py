"""Time utilities"""
from datetime import datetime


def format_timestamp(dt: datetime = None) -> str:
    """Format timestamp to ISO format"""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable"""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''}"
