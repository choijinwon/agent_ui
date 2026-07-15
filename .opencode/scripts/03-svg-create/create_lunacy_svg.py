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


def render_icon(name: str, x: float, y: float, color: str, size: int = 16) -> str:
    stroke = f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    if name == "home":
        return f'<path d="M{x+2} {y+8} L{x+size/2} {y+2} L{x+size-2} {y+8} V{y+size-2} H{x+5} V{y+10} H{x+size-5} V{y+size-2} H{x+2} Z" fill="none" {stroke} />'
    if name == "chart":
        return "\n".join([
            f'<line x1="{x+2}" y1="{y+size-2}" x2="{x+size-2}" y2="{y+size-2}" {stroke} />',
            f'<polyline points="{x+3},{y+11} {x+7},{y+7} {x+10},{y+9} {x+14},{y+4}" fill="none" {stroke} />',
        ])
    if name == "wallet":
        return "\n".join([
            rounded_rect(int(x + 1), int(y + 4), size - 2, size - 7, "none", color, 3),
            f'<circle cx="{x+size-4}" cy="{y+size/2+1}" r="1.5" fill="{color}" />',
        ])
    if name == "settings":
        return "\n".join([
            f'<circle cx="{x+size/2}" cy="{y+size/2}" r="3" fill="none" {stroke} />',
            f'<circle cx="{x+size/2}" cy="{y+size/2}" r="7" fill="none" {stroke} stroke-dasharray="2 4" />',
        ])
    if name == "spark":
        return f'<path d="M{x+8} {y+1} L{x+10} {y+6} L{x+15} {y+8} L{x+10} {y+10} L{x+8} {y+15} L{x+6} {y+10} L{x+1} {y+8} L{x+6} {y+6} Z" fill="{color}" />'
    return f'<circle cx="{x+size/2}" cy="{y+size/2}" r="{size/3}" fill="{color}" />'


def render_sidebar(c: dict, colors: dict) -> str:
    return rounded_rect(c["x"], c["y"], c["w"], c["h"], c.get("fill", colors["surface"]), colors["line"], 12)


def render_nav_item(c: dict, colors: dict) -> str:
    fill = colors["surface_alt"] if c.get("active") else "transparent"
    text_fill = colors["text"] if c.get("active") else colors["muted"]
    icon = render_icon(c.get("icon", "home"), c["x"] + 12, c["y"] + 12, text_fill, 16)
    return "\n".join([
        rounded_rect(c["x"], c["y"], c["w"], c["h"], fill, None, 8),
        icon,
        text_element(c["x"] + 38, c["y"] + 8, c["text"], 14, text_fill, 600, c["w"] - 50),
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
        rounded_rect(c["x"] + c["w"] - 56, c["y"] + 18, 36, 36, colors["surface_alt"], None, 8),
        render_icon(c.get("icon", "chart"), c["x"] + c["w"] - 46, c["y"] + 28, colors["primary"], 16),
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
    icons = c.get("icons", ["home", "chart", "wallet", "settings"])
    parts = [rounded_rect(c["x"], c["y"], c["w"], c["h"], c.get("fill", colors["surface"]), colors["line"], 18)]
    step = c["w"] / len(labels)
    for index, label in enumerate(labels):
        cx = c["x"] + step * index + step / 2
        fill = colors["primary"] if index == 0 else colors["muted"]
        parts.append(render_icon(icons[index] if index < len(icons) else "home", cx - 8, c["y"] + 13, fill, 16))
        parts.append(f'<text x="{cx:.1f}" y="{c["y"] + 46}" font-family="Inter, Arial, sans-serif" font-size="11" font-weight="600" text-anchor="middle" fill="{fill}">{esc(label)}</text>')
    return "\n".join(parts)


def render_tabs(c: dict, colors: dict) -> str:
    labels = c.get("labels", [])
    active = int(c.get("active", 0))
    parts = [rounded_rect(c["x"], c["y"], c["w"], c["h"], colors["surface"], colors["line"], 8)]
    if not labels:
        return "\n".join(parts)
    tab_w = c["w"] / len(labels)
    for i, label in enumerate(labels):
        x = c["x"] + i * tab_w + 4
        fill = colors["surface_alt"] if i == active else "transparent"
        text_fill = colors["text"] if i == active else colors["muted"]
        parts.append(rounded_rect(int(x), c["y"] + 4, int(tab_w - 8), c["h"] - 8, fill, None, 6))
        parts.append(f'<text x="{x + tab_w/2 - 4:.1f}" y="{c["y"] + 28}" font-family="Inter, Arial, sans-serif" font-size="13" font-weight="700" text-anchor="middle" fill="{text_fill}">{esc(label)}</text>')
    return "\n".join(parts)


def render_dropdown(c: dict, colors: dict) -> str:
    return "\n".join([
        rounded_rect(c["x"], c["y"], c["w"], c["h"], colors["surface"], colors["line"], 8),
        text_element(c["x"] + 14, c["y"] + 6, c.get("label", "Select"), 11, colors["muted"], 700, c["w"] - 28),
        text_element(c["x"] + 14, c["y"] + 24, c.get("value", "Option"), 15, colors["text"], 700, c["w"] - 48),
        f'<path d="M{c["x"] + c["w"] - 28} {c["y"] + 24} L{c["x"] + c["w"] - 20} {c["y"] + 32} L{c["x"] + c["w"] - 12} {c["y"] + 24}" fill="none" stroke="{colors["muted"]}" stroke-width="2" />',
    ])


def render_table(c: dict, colors: dict) -> str:
    x, y, w, h = c["x"], c["y"], c["w"], c["h"]
    rows = c.get("rows", [])
    cols = c.get("columns", [])
    col_w = w / max(1, len(cols))
    row_h = 44
    parts = [rounded_rect(x, y, w, h, colors["surface"], colors["line"], 8)]
    parts.append(rounded_rect(x, y, w, 48, colors["surface_alt"], None, 8))
    for i, col in enumerate(cols):
        parts.append(text_element(int(x + i * col_w + 16), y + 15, col, 13, colors["muted"], 800, int(col_w - 24)))
    for r, row in enumerate(rows):
        ry = y + 48 + r * row_h
        parts.append(f'<line x1="{x}" y1="{ry}" x2="{x+w}" y2="{ry}" stroke="{colors["line"]}" />')
        for i, value in enumerate(row):
            parts.append(text_element(int(x + i * col_w + 16), ry + 12, value, 13, colors["text"], 600, int(col_w - 24)))
    return "\n".join(parts)


def render_form(c: dict, colors: dict) -> str:
    x, y, w, h = c["x"], c["y"], c["w"], c["h"]
    parts = [rounded_rect(x, y, w, h, colors["surface"], colors["line"], 8)]
    parts.append(text_element(x + 18, y + 18, c.get("title", "Form"), 17, colors["text"], 800, w - 36))
    for i, field in enumerate(c.get("fields", [])):
        fy = y + 64 + i * 62
        parts.append(text_element(x + 18, fy - 18, field, 12, colors["muted"], 700, w - 36))
        parts.append(rounded_rect(x + 18, fy, w - 36, 42, colors["surface_alt"], colors["line"], 6))
    parts.append(rounded_rect(x + 18, y + h - 58, 132, 40, colors["primary"], None, 8))
    parts.append(text_element(x + 42, y + h - 48, c.get("action", "Submit"), 14, "#FFFFFF", 800, 100))
    return "\n".join(parts)


def render_modal(c: dict, colors: dict) -> str:
    x, y, w, h = c["x"], c["y"], c["w"], c["h"]
    actions = c.get("actions", ["Cancel", "Confirm"])
    parts = [
        rounded_rect(x, y, w, h, colors["surface"], colors["line"], 12),
        text_element(x + 20, y + 22, c.get("title", "Modal"), 18, colors["text"], 800, w - 40),
        text_element(x + 20, y + 64, c.get("body", ""), 14, colors["muted"], 400, w - 40),
    ]
    button_w = 94
    for i, action in enumerate(actions[-2:]):
        bx = x + w - 20 - (len(actions[-2:]) - i) * (button_w + 10)
        fill = colors["primary"] if i == len(actions[-2:]) - 1 else colors["surface_alt"]
        text_fill = "#FFFFFF" if fill == colors["primary"] else colors["text"]
        parts.append(rounded_rect(bx, y + h - 58, button_w, 38, fill, None, 8))
        parts.append(text_element(bx + 16, y + h - 49, action, 13, text_fill, 800, button_w - 24))
    return "\n".join(parts)


def render_toast(c: dict, colors: dict) -> str:
    tone = c.get("tone", "success")
    tone_color = colors.get(tone, colors["primary"])
    return "\n".join([
        rounded_rect(c["x"], c["y"], c["w"], c["h"], colors["surface"], colors["line"], 8),
        rounded_rect(c["x"], c["y"], 5, c["h"], tone_color, None, 3),
        text_element(c["x"] + 18, c["y"] + 9, c.get("title", "Notice"), 14, colors["text"], 800, c["w"] - 36),
        text_element(c["x"] + 18, c["y"] + 29, c.get("detail", ""), 12, colors["muted"], 500, c["w"] - 36),
    ])


def render_pricing_card(c: dict, colors: dict) -> str:
    x, y, w, h = c["x"], c["y"], c["w"], c["h"]
    parts = [rounded_rect(x, y, w, h, colors["surface"], colors["line"], 10)]
    parts.append(text_element(x + 20, y + 18, c.get("title", "Plan"), 17, colors["text"], 800, w - 40))
    parts.append(text_element(x + 20, y + 52, c.get("price", "$0"), 34, colors["primary"], 900, w - 40))
    for i, feature in enumerate(c.get("features", [])):
        fy = y + 104 + i * 24
        parts.append(f'<circle cx="{x+26}" cy="{fy+5}" r="4" fill="{colors["success"]}" />')
        parts.append(text_element(x + 40, fy - 6, feature, 13, colors["text"], 600, w - 60))
    return "\n".join(parts)


def render_calendar(c: dict, colors: dict) -> str:
    x, y, w, h = c["x"], c["y"], c["w"], c["h"]
    parts = [rounded_rect(x, y, w, h, colors["surface"], colors["line"], 8)]
    parts.append(text_element(x + 18, y + 16, c.get("title", "Calendar"), 17, colors["text"], 800, w - 36))
    selected = set(c.get("selected", []))
    cell_w = (w - 36) / 7
    for day in range(1, 29):
        col = (day - 1) % 7
        row = (day - 1) // 7
        cx = x + 18 + col * cell_w
        cy = y + 62 + row * 42
        fill = colors["primary"] if day in selected else colors["surface_alt"]
        text_fill = "#FFFFFF" if day in selected else colors["text"]
        parts.append(rounded_rect(int(cx), int(cy), int(cell_w - 6), 34, fill, None, 6))
        parts.append(f'<text x="{cx + cell_w/2 - 3:.1f}" y="{cy + 22}" font-family="Inter, Arial, sans-serif" font-size="12" font-weight="700" text-anchor="middle" fill="{text_fill}">{day}</text>')
    return "\n".join(parts)


def render_kanban(c: dict, colors: dict) -> str:
    x, y, w, h = c["x"], c["y"], c["w"], c["h"]
    columns = c.get("columns", [])
    gap = 12
    col_w = (w - gap * max(0, len(columns) - 1)) / max(1, len(columns))
    parts = []
    for i, col in enumerate(columns):
        cx = x + i * (col_w + gap)
        parts.append(rounded_rect(int(cx), y, int(col_w), h, colors["surface"], colors["line"], 8))
        parts.append(text_element(int(cx + 14), y + 14, col.get("title", "Column"), 14, colors["text"], 800, int(col_w - 28)))
        for j, item in enumerate(col.get("items", [])):
            iy = y + 52 + j * 52
            parts.append(rounded_rect(int(cx + 12), iy, int(col_w - 24), 40, colors["surface_alt"], colors["line"], 6))
            parts.append(text_element(int(cx + 24), iy + 11, item, 12, colors["text"], 600, int(col_w - 48)))
    return "\n".join(parts)


def render_image_placeholder(c: dict, colors: dict) -> str:
    x, y, w, h = c["x"], c["y"], c["w"], c["h"]
    return "\n".join([
        rounded_rect(x, y, w, h, colors["surface_alt"], colors["line"], 10),
        f'<line x1="{x+18}" y1="{y+18}" x2="{x+w-18}" y2="{y+h-18}" stroke="{colors["line"]}" stroke-width="2" />',
        f'<line x1="{x+w-18}" y1="{y+18}" x2="{x+18}" y2="{y+h-18}" stroke="{colors["line"]}" stroke-width="2" />',
        text_element(x + 20, y + h - 42, c.get("label", "Image asset"), 13, colors["muted"], 700, w - 40),
    ])


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
        "tabs": render_tabs,
        "dropdown": render_dropdown,
        "table": render_table,
        "form": render_form,
        "modal": render_modal,
        "toast": render_toast,
        "pricing_card": render_pricing_card,
        "calendar": render_calendar,
        "kanban": render_kanban,
        "image_placeholder": render_image_placeholder,
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
