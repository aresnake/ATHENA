"""Math helper stubs for geometry operations."""

def clamp(value, minimum, maximum):
    """Clamp numeric value to [minimum, maximum]."""
    return max(minimum, min(maximum, value))

