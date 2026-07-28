def get_severity(value):
    """
    Maps a usage percentage to a severity level.
    Returns None if the value is healthy (no incident needed).
    """
    if value >= 95:
        return "HIGH"
    elif value >= 90:
        return "MEDIUM"
    elif value >= 80:
        return "LOW"
    return None