"""
Human Design Bodygraph SVG Generator
=====================================

Generates a beautiful, detailed bodygraph visualization with:
- 9 centers (colored by definition)
- Active channels (colored by type)
- Gate numbers (black/red for personality/design)
- Center labels
- Full color scheme

Usage:
    from src.hd_bodygraph import generate_bodygraph_svg
    svg = generate_bodygraph_svg(hd_chart)
"""

from typing import Optional
from encoders.human_design_full import GATES


# Center positions in the bodygraph (x, y) — standard HD layout
CENTER_POSITIONS = {
    "Head":       (400, 60),
    "Ajna":       (400, 140),
    "Throat":     (400, 240),
    "G":          (400, 340),
    "Heart/Will": (280, 340),
    "Solar Plexus": (520, 420),
    "Sacral":     (400, 480),
    "Splenic":    (260, 420),
    "Root":       (400, 560),
}

# Center shapes (width, height for rectangles, radius for circles)
CENTER_SHAPES = {
    "Head":       {"type": "triangle_up", "size": 70},
    "Ajna":       {"type": "triangle_down", "size": 70},
    "Throat":     {"type": "square", "size": 60},
    "G":          {"type": "diamond", "size": 70},
    "Heart/Will": {"type": "triangle_up", "size": 50},
    "Solar Plexus": {"type": "triangle_right", "size": 60},
    "Sacral":     {"type": "square", "size": 60},
    "Splenic":    {"type": "triangle_left", "size": 60},
    "Root":       {"type": "square", "size": 60},
}

# Channel connections (gate1, gate2) -> line coordinates
# Standard bodygraph line positions (approximate)
CHANNEL_LINES = {
    # Head to Ajna
    (64, 47): ((400, 95), (400, 110)),
    (61, 24): ((370, 95), (370, 110)),
    (63, 4): ((430, 95), (430, 110)),
    # Ajna to Throat
    (17, 62): ((380, 175), (380, 210)),
    (43, 23): ((420, 175), (420, 210)),
    (11, 56): ((400, 175), (400, 210)),
    # Throat to G
    (1, 8): ((380, 270), (380, 310)),
    (7, 31): ((420, 270), (420, 310)),
    (13, 33): ((400, 270), (400, 310)),
    # Throat to Heart/Will
    (45, 21): ((350, 270), (310, 310)),
    # Throat to Solar Plexus
    (12, 22): ((450, 270), (490, 310)),
    (35, 36): ((460, 270), (500, 310)),
    # Throat to Sacral
    (20, 34): ((400, 270), (400, 450)),
    (20, 57): ((400, 270), (400, 450)),
    # G to Solar Plexus
    (2, 14): ((430, 370), (490, 390)),
    # G to Sacral
    (15, 5): ((380, 370), (380, 450)),
    (10, 34): ((420, 370), (420, 450)),
    (29, 46): ((400, 370), (400, 450)),
    # G to Splenic
    (10, 57): ((360, 370), (290, 390)),
    # Heart/Will to Throat (already covered above)
    # Heart/Will to Solar Plexus
    (37, 40): ((310, 370), (490, 390)),
    # Solar Plexus to Root
    (49, 19): ((510, 450), (420, 530)),
    (55, 39): ((530, 450), (440, 530)),
    (30, 41): ((500, 450), (400, 530)),
    # Solar Plexus to Sacral
    (6, 59): ((500, 450), (420, 450)),
    # Splenic to Root
    (38, 28): ((270, 450), (380, 530)),
    (54, 32): ((290, 450), (400, 530)),
    (58, 18): ((280, 450), (370, 530)),
    # Splenic to Sacral
    (27, 50): ((290, 450), (380, 450)),
    (34, 57): ((310, 450), (390, 450)),
    # Splenic to Heart/Will
    (26, 44): ((270, 390), (280, 310)),
    # Root to Sacral
    (42, 53): ((390, 530), (390, 450)),
    (3, 60): ((410, 530), (410, 450)),
}


def generate_bodygraph_svg(
    chart,
    width: int = 800,
    height: int = 620,
    dark_bg: bool = True,
) -> str:
    """Generate an SVG bodygraph from a HumanDesignChart object."""
    
    # Get defined centers and gates
    defined_centers = {c.name for c in chart.centers if c.is_defined}
    personality_gates = {g.gate for g in chart.personality_gates}
    design_gates = {g.gate for g in chart.design_gates}
    active_channels = set()
    for ch in chart.channels:
        g1, g2 = ch["gates"]
        active_channels.add((min(g1, g2), max(g1, g2)))

    # Color scheme
    bg = "#0a0a0a" if dark_bg else "#ffffff"
    text_color = "#ffffff" if dark_bg else "#000000"
    
    # Center colors
    defined_color = "#4fc3f7"
    undefined_color = "#333333" if dark_bg else "#e0e0e0"
    defined_stroke = "#81d4fa"
    undefined_stroke = "#555555" if dark_bg else "#cccccc"
    
    # Channel colors
    channel_color = "#4fc3f7"
    
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{bg}"/>',
    ]

    # Draw channel lines (behind centers)
    for (g1, g2), ((x1, y1), (x2, y2)) in CHANNEL_LINES.items():
        is_active = (min(g1, g2), max(g1, g2)) in active_channels
        if is_active:
            svg_parts.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{channel_color}" stroke-width="3" opacity="0.8"/>'
            )
        else:
            svg_parts.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{undefined_stroke}" stroke-width="1" opacity="0.3"/>'
            )

    # Draw gate numbers along channels
    for (g1, g2), ((x1, y1), (x2, y2)) in CHANNEL_LINES.items():
        is_active = (min(g1, g2), max(g1, g2)) in active_channels
        if is_active:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            
            # Gate 1 color
            g1_color = "#000000" if g1 in personality_gates else "#ff4444" if g1 in design_gates else "#888888"
            g2_color = "#000000" if g2 in personality_gates else "#ff4444" if g2 in design_gates else "#888888"
            
            svg_parts.append(
                f'<text x="{mid_x - 8}" y="{mid_y}" fill="{g1_color}" font-size="8" '
                f'font-family="monospace" text-anchor="middle" font-weight="bold">{g1}</text>'
            )
            svg_parts.append(
                f'<text x="{mid_x + 8}" y="{mid_y}" fill="{g2_color}" font-size="8" '
                f'font-family="monospace" text-anchor="middle" font-weight="bold">{g2}</text>'
            )

    # Draw centers
    for center_name, (cx, cy) in CENTER_POSITIONS.items():
        is_defined = center_name in defined_centers
        shape = CENTER_SHAPES[center_name]
        
        fill = defined_color if is_defined else bg
        stroke = defined_stroke if is_defined else undefined_stroke
        stroke_width = 2 if is_defined else 1
        
        if shape["type"] == "square":
            s = shape["size"] / 2
            svg_parts.append(
                f'<rect x="{cx - s}" y="{cy - s}" width="{shape["size"]}" height="{shape["size"]}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" rx="4"/>'
            )
        elif shape["type"] == "diamond":
            s = shape["size"] / 2
            points = f"{cx},{cy - s} {cx + s},{cy} {cx},{cy + s} {cx - s},{cy}"
            svg_parts.append(
                f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
            )
        elif shape["type"] == "triangle_up":
            s = shape["size"] / 2
            points = f"{cx},{cy - s} {cx - s},{cy + s} {cx + s},{cy + s}"
            svg_parts.append(
                f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
            )
        elif shape["type"] == "triangle_down":
            s = shape["size"] / 2
            points = f"{cx - s},{cy - s} {cx + s},{cy - s} {cx},{cy + s}"
            svg_parts.append(
                f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
            )
        elif shape["type"] == "triangle_right":
            s = shape["size"] / 2
            points = f"{cx - s},{cy - s} {cx + s},{cy} {cx - s},{cy + s}"
            svg_parts.append(
                f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
            )
        elif shape["type"] == "triangle_left":
            s = shape["size"] / 2
            points = f"{cx + s},{cy - s} {cx - s},{cy} {cx + s},{cy + s}"
            svg_parts.append(
                f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
            )

        # Center label
        label = center_name.replace("/", "\n")
        svg_parts.append(
            f'<text x="{cx}" y="{cy + 3}" fill="{text_color}" font-size="9" '
            f'font-family="monospace" text-anchor="middle" font-weight="bold">{center_name}</text>'
        )

    # Gate numbers around centers (personality = black, design = red)
    for gate in personality_gates:
        if gate in GATES:
            center = GATES[gate]["center"]
            if center in CENTER_POSITIONS:
                cx, cy = CENTER_POSITIONS[center]
                # Offset based on gate number
                offset_x = ((gate * 7) % 40) - 20
                offset_y = ((gate * 13) % 30) - 15
                svg_parts.append(
                    f'<text x="{cx + offset_x}" y="{cy + offset_y}" fill="#000000" font-size="7" '
                    f'font-family="monospace" text-anchor="middle">{gate}</text>'
                )

    for gate in design_gates:
        if gate in GATES:
            center = GATES[gate]["center"]
            if center in CENTER_POSITIONS:
                cx, cy = CENTER_POSITIONS[center]
                offset_x = ((gate * 11) % 40) - 20
                offset_y = ((gate * 17) % 30) - 15
                svg_parts.append(
                    f'<text x="{cx + offset_x}" y="{cy + offset_y}" fill="#ff4444" font-size="7" '
                    f'font-family="monospace" text-anchor="middle">{gate}</text>'
                )

    # Title
    svg_parts.append(
        f'<text x="{width/2}" y="25" fill="{text_color}" font-size="14" '
        f'font-family="monospace" text-anchor="middle" font-weight="bold">'
        f'{chart.hd_type} | {chart.profile_number[0]}.{chart.profile_number[1]} | {chart.authority} Authority</text>'
    )

    # Type label
    svg_parts.append(
        f'<text x="{width/2}" y="{height - 10}" fill="#666666" font-size="10" '
        f'font-family="monospace" text-anchor="middle">'
        f'Strategy: {chart.strategy} | Not-Self: {chart.not_self_theme} | Signature: {chart.signature}</text>'
    )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)
