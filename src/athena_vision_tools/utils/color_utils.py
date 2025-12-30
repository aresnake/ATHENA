"""Color helper stubs for heatmaps and overlays."""

def to_rgba(color, default=(1.0, 1.0, 1.0, 1.0)):
    """Ensure a 4-tuple RGBA."""
    if not color:
        return default
    if len(color) == 3:
        return (color[0], color[1], color[2], 1.0)
    return tuple(color)

