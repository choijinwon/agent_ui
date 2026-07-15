#!/usr/bin/env python3
import argparse
import html
import json
from pathlib import Path


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def attrs(**values: object) -> str:
    parts = []
    for key, value in values.items():
        if value is None:
            continue
        parts.append(f'{key.replace("_", "-")}="{esc(value)}"')
    return " ".join(parts)


def text_element(x: int, y: int, text: str, size: int, fill: str, weight: int = 400, width: int | None = None) -> str:
    max_chars = max(12, int((width or 420) / (size * 0.52)))
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    if not lines:
        lines = [text]
    tspans = []
    for index, line in enumerate(lines[:3]):
        dy = 0 if index == 0 else int(size * 1.28)
        tspans.append(f'<tspan x="{x}" dy="{dy}">{esc(line)}</tspan>')
    return (
        f'<text x="{x}" y="{y + size}" font-family="Inter, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{"".join(tspans)}</text>'
    )


def rounded_rect(x: int, y: int, w: int, h: int, fill: str, stroke: str | None = None, radius: int = 8, opacity: float | None = None) -> str:
    return f'<rect {attrs(x=x, y=y, width=w, height=h, rx=radius, fill=fill, stroke=stroke, opacity=opacity)} />'


def render_sidebar(c: dict, colors: dict) -> str:
    return rounded_rect(c["x"], c["y"], c["w"], c["h"], c.get("fill", colors["surface"]), colors["line"], 12)


def render_nav_item(c: dict, colors: dict) -> str:
    fill = colors["surface_alt"] if c.get("active") else "transparent"
    text_fill = colors["text"] if c.get("active") else colors["muted"]
    return "\n".join([
        rounded_rect(c["x"], c["y"], c["w"], c["h"], fill, None, 8),
        text_element(c["x"] + 14, c["y"] + 8, c["text"], 14, text_fill, 600, c["w"] - 28),
    ])


def render_button(c: dict, colors: dict) -> str:
    fill = c.get("fill", colors["primary"])
    return "\n".join([
        rounded_rect(c["x"], c["y"], c["w"], c["h"], fill, None, 8),
        f'<text x="{c["x"] + c["w"] / 2}" y="{c["y"] + c["h"] / 2 + 5}" '
        f'font-family="Inter, Arial, sans-serif" font-size="14" font-weight="700" '
        f'text-anchor="middle" fill="#FFFFFF">{esc(c["text"])}</text>',
    ])


def render_metric_card(c: dict, colors: dict) -> str:
    return "\n".join([
        rounded_rect(c["x"], c["y"], c["w"], c["h"], colors["surface"], colors["line"], 10),
        text_element(c["x"] + 20, c["y"] + 18, c["label"], 13, colors["muted"], 600, c["w"] - 40),
        text_element(c["x"] + 20, c["y"] + 48, c["value"], 30, colors["text"], 800, c["w"] - 40),
        text_element(c["x"] + c["w"] - 78, c["y"] + 76, c["trend"], 13, colors["success"], 700, 70),
    ])


def render_chart_card(c: dict, colors: dict) -> str:
    x, y, w, h = c["x"], c["y"], c["w"], c["h"]
    values = c.get("values", [20, 40, 30, 70])
    max_v = max(values) or 1
    min_v = min(values)
    spread = max(1, max_v - min_v)
    points = []
    pad_x, pad_top, pad_bottom = 24, 72, 32
    for index, value in enumerate(values):
        px = x + pad_x + index * ((w - pad_x * 2) / max(1, len(values) - 1))
        py = y + pad_top + (1 - ((value - min_v) / spread)) * (h - pad_top - pad_bottom)
        points.append(f"{px:.1f},{py:.1f}")
    grid = []
    for i in range(4):
        gy = y + pad_top + i * ((h - pad_top - pad_bottom) / 3)
        grid.append(f'<line x1="{x + pad_x}" y1="{gy:.1f}" x2="{x + w - pad_x}" y2="{gy:.1f}" stroke="{colors["line"]}" stroke-width="1" />')
    dots = []
    for point in points:
        px, py = point.split(",")
        dots.append(f'<circle cx="{px}" cy="{py}" r="4" fill="{colors["primary"]}" />')
    return "\n".join([
        rounded_rect(x, y, w, h, colors["surface"], colors["line"], 10),
        text_element(x + 20, y + 18, c.get("title", "Trend"), 17, colors["text"], 700, w - 40),
        *grid,
        f'<polyline points="{" ".join(points)}" fill="none" stroke="{colors["primary"]}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />',
        *dots,
    ])


def render_search(c: dict, colors: dict) -> str:
    return "\n".join([
        rounded_rect(c["x"], c["y"], c["w"], c["h"], colors["surface"], colors["line"], 8),
        f'<circle cx="{c["x"] + 22}" cy="{c["y"] + 24}" r="7" fill="none" stroke="{colors["muted"]}" stroke-width="2" />',
        f'<line x1="{c["x"] + 28}" y1="{c["y"] + 30}" x2="{c["x"] + 35}" y2="{c["y"] + 37}" stroke="{colors["muted"]}" stroke-width="2" stroke-linecap="round" />',
        text_element(c["x"] + 48, c["y"] + 13, c.get("placeholder", "Search"), 14, colors["muted"], 400, c["w"] - 64),
    ])


def render_list_row(c: dict, colors: dict) -> str:
    return "\n".join([
        rounded_rect(c["x"], c["y"], c["w"], c["h"], colors["surface"], colors["line"], 8),
        rounded_rect(c["x"] + 16, c["y"] + 18, 36, 36, colors["surface_alt"], None, 8),
        text_element(c["x"] + 68, c["y"] + 12, c["title"], 16, colors["text"], 700, c["w"] - 92),
        text_element(c["x"] + 68, c["y"] + 38, c["detail"], 13, colors["muted"], 400, c["w"] - 92),
    ])


def render_inspector(c: dict, colors: dict) -> str:
    return "\n".join([
        rounded_rect(c["x"], c["y"], c["w"], c["h"], colors["surface_alt"], colors["line"], 10),
        text_element(c["x"] + 20, c["y"] + 20, c["title"], 18, colors["text"], 800, c["w"] - 40),
        text_element(c["x"] + 20, c["y"] + 58, c["body"], 15, colors["muted"], 400, c["w"] - 40),
        rounded_rect(c["x"] + 20, c["y"] + 118, c["w"] - 40, 56, colors["surface"], colors["line"], 8),
        text_element(c["x"] + 36, c["y"] + 132, '"components[0].text": "..."', 13, colors["muted"], 500, c["w"] - 72),
    ])


def render_toggle_row(c: dict, colors: dict) -> str:
    knob_x = c["x"] + c["w"] - 52 if c.get("enabled") else c["x"] + c["w"] - 78
    track_fill = colors["primary"] if c.get("enabled") else colors["line"]
    return "\n".join([
        rounded_rect(c["x"], c["y"], c["w"], c["h"], colors["surface"], colors["line"], 8),
        text_element(c["x"] + 18, c["y"] + 18, c["title"], 15, colors["text"], 700, c["w"] - 110),
        rounded_rect(c["x"] + c["w"] - 86, c["y"] + 18, 64, 30, track_fill, None, 15),
        f'<circle cx="{knob_x}" cy="{c["y"] + 33}" r="12" fill="#FFFFFF" />',
    ])


def render_bottom_nav(c: dict, colors: dict) -> str:
    labels = c.get("labels", ["Home", "Search", "Saved", "Settings"])
    parts = [rounded_rect(c["x"], c["y"], c["w"], c["h"], c.get("fill", colors["surface"]), colors["line"], 18)]
    step = c["w"] / len(labels)
    for index, label in enumerate(labels):
        cx = c["x"] + step * index + step / 2
        fill = colors["primary"] if index == 0 else colors["muted"]
        parts.append(f'<circle cx="{cx:.1f}" cy="{c["y"] + 22}" r="5" fill="{fill}" />')
        parts.append(f'<text x="{cx:.1f}" y="{c["y"] + 46}" font-family="Inter, Arial, sans-serif" font-size="11" font-weight="600" text-anchor="middle" fill="{fill}">{esc(label)}</text>')
    return "\n".join(parts)


def render_component(c: dict, colors: dict) -> str:
    kind = c["type"]
    if kind == "text":
        fill = colors["muted"] if c.get("role") in {"eyebrow", "body"} else colors["text"]
        if c.get("role") == "eyebrow":
            fill = colors["primary"]
        return text_element(c["x"], c["y"], c["text"], c.get("size", 16), fill, c.get("weight", 400), c.get("w"))
    renderers = {
        "sidebar": render_sidebar,
        "nav_item": render_nav_item,
        "button": render_button,
        "metric_card": render_metric_card,
        "chart_card": render_chart_card,
        "search": render_search,
        "list_row": render_list_row,
        "inspector": render_inspector,
        "toggle_row": render_toggle_row,
        "bottom_nav": render_bottom_nav,
    }
    renderer = renderers.get(kind)
    if not renderer:
        return rounded_rect(c["x"], c["y"], c["w"], c["h"], colors["surface"], colors["line"], 8)
    return renderer(c, colors)


def render_svg(spec: dict) -> str:
    colors = spec["tokens"]["colors"]
    frames = spec["frames"]
    gap = 80
    total_w = sum(frame["w"] for frame in frames) + gap * (len(frames) + 1)
    total_h = max(frame["h"] for frame in frames) + 160
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}">',
        f'<title>{esc(spec.get("name", "Lunacy Design"))}</title>',
        '<desc>Generated by Lunacy Design Agent. Open this SVG in Lunacy for editable vector layers.</desc>',
        '<rect width="100%" height="100%" fill="#DDE3EC" />',
    ]
    cursor_x = gap
    for frame in frames:
        frame_y = 72
        parts.append(f'<g id="{esc(frame["id"])}" data-layer-name="{esc(frame["name"])}" transform="translate({cursor_x},{frame_y})">')
        parts.append(f'<text x="0" y="-22" font-family="Inter, Arial, sans-serif" font-size="18" font-weight="800" fill="#172033">{esc(frame["name"])}</text>')
        parts.append(rounded_rect(0, 0, frame["w"], frame["h"], colors["canvas"], None, 18))
        for comp in frame["components"]:
            parts.append(f'<g id="{esc(comp["id"])}" data-component-type="{esc(comp["type"])}" data-layer-name="{esc(comp["id"])}">')
            parts.append(render_component(comp, colors))
            parts.append("</g>")
        parts.append("</g>")
        cursor_x += frame["w"] + gap
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render_html(svg_path: Path, spec: dict) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(spec.get("name", "Lunacy Design Preview"))}</title>
  <style>
    body {{ margin: 0; background: #dfe5ee; font-family: Inter, Arial, sans-serif; }}
    header {{ padding: 18px 24px; background: #fff; border-bottom: 1px solid #cad3df; }}
    main {{ overflow: auto; padding: 24px; }}
    img {{ display: block; max-width: none; box-shadow: 0 18px 48px rgba(23,32,51,.18); }}
  </style>
</head>
<body>
  <header><strong>{esc(spec.get("name", "Lunacy Design"))}</strong> - SVG preview</header>
  <main><img src="{esc(svg_path.name)}" alt="Generated Lunacy design"></main>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--html")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    spec_path = Path(args.spec)
    if not spec_path.is_absolute():
        spec_path = project / spec_path
    output = Path(args.output)
    if not output.is_absolute():
        output = project / output
    if output.exists() and not args.force:
        raise SystemExit(f"{output} already exists. Use --force to overwrite.")

    spec = load_json(spec_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_svg(spec), encoding="utf-8")

    if args.html:
        html_path = Path(args.html)
        if not html_path.is_absolute():
            html_path = project / html_path
        if html_path.exists() and not args.force:
            raise SystemExit(f"{html_path} already exists. Use --force to overwrite.")
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(render_html(output, spec), encoding="utf-8")
        print(f"Wrote {html_path}")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
