from pathlib import Path

def generate_badge(score: int, grade: str, output_path: Path):
    """
    Generate a simple SVG badge for the security score.
    
    Args:
        score: Health score (0-100)
        grade: Letter grade (A-F)
        output_path: Path to save the SVG file
    """
    
    # Determine color based on grade
    colors = {
        "A": "#4c1", # Green
        "B": "#97ca00", # Light Green
        "C": "#dfb317", # Yellow
        "D": "#fe7d37", # Orange
        "E": "#e05d44", # Red
        "F": "#e05d44"  # Red
    }
    color = colors.get(grade, "#9f9f9f") # Grey default
    
    # Simple SVG Template (Shields.io style)
    # Width calculations are approximate but sufficient for standard text
    width = 90
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="20" role="img" aria-label="security: {grade}">
    <title>security: {grade}</title>
    <linearGradient id="s" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <clipPath id="r">
        <rect width="{width}" height="20" rx="3" fill="#fff"/>
    </clipPath>
    <g clip-path="url(#r)">
        <rect width="55" height="20" fill="#555"/>
        <rect x="55" width="35" height="20" fill="{color}"/>
        <rect width="{width}" height="20" fill="url(#s)"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
        <text aria-hidden="true" x="285" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="450">security</text>
        <text x="285" y="140" transform="scale(.1)" fill="#fff" textLength="450">security</text>
        <text aria-hidden="true" x="715" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="250">{grade} ({score})</text>
        <text x="715" y="140" transform="scale(.1)" fill="#fff" textLength="250">{grade} ({score})</text>
    </g>
</svg>"""

    try:
        output_path.write_text(svg, encoding="utf-8")
        return True
    except Exception as e:
        print(f"⚠️  Failed to save badge: {e}")
        return False
