CHANNEL_PALETTE = [
    "#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF",
    "#F15BB5", "#C1FBA4", "#9B5DE5", "#00F5D4",
    "#FEE440", "#F94144", "#90BE6D", "#577590",
    "#43AA8B", "#F3722C", "#277DA1", "#E76F51",
]

def pitch_to_color_hex(pitch, pmin, pmax):
    if pmin is None or pmax is None or pmin == pmax:
        return "#00F5D4"
    t = (pitch - pmin) / float(max(1, (pmax - pmin)))
    t = max(0.0, min(1.0, t))
    r = int(60 + (255-60)*t)
    g = int(80 + (85-80)*t)
    b = int(220 + (170-220)*t)
    return f"#{r:02X}{g:02X}{b:02X}"

def channel_color(channel: int) -> str:
    try:
        return CHANNEL_PALETTE[channel % 16]
    except Exception:
        return "#FFFFFF"
