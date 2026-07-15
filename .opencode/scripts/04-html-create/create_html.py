#!/usr/bin/env python3
import argparse
import html
import json
from pathlib import Path


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def css_vars(colors: dict) -> str:
    return "\n".join(f"  --color-{name}: {value};" for name, value in colors.items())


def style_attr(component: dict) -> str:
    props = [
        "position:absolute",
        f"left:{component['x']}px",
        f"top:{component['y']}px",
        f"width:{component['w']}px",
        f"height:{component['h']}px",
    ]
    return ";".join(props)


def data_attrs(component: dict) -> str:
    return f'data-layer-id="{esc(component["id"])}" data-component-type="{esc(component["type"])}"'


def render_text(c: dict) -> str:
    role = c.get("role", "body")
    tag = "h1" if role == "headline" else "p"
    cls = f"text text-{role}"
    return f'<{tag} class="{cls}" {data_attrs(c)} style="{style_attr(c)}">{esc(c.get("text", ""))}</{tag}>'


def render_button(c: dict) -> str:
    return f'<button class="button button-{esc(c.get("tone", "default"))}" {data_attrs(c)} style="{style_attr(c)}">{esc(c.get("text", "Button"))}</button>'


def render_sidebar(c: dict) -> str:
    return f'<nav class="sidebar" aria-label="Primary" {data_attrs(c)} style="{style_attr(c)}"></nav>'


def render_nav_item(c: dict) -> str:
    active = " is-active" if c.get("active") else ""
    return f'<a class="nav-item{active}" href="#" {data_attrs(c)} style="{style_attr(c)}">{esc(c.get("text", "Item"))}</a>'


def render_bottom_nav(c: dict) -> str:
    labels = c.get("labels", [])
    items = "".join(f'<a href="#" class="bottom-nav-item{" is-active" if i == 0 else ""}">{esc(label)}</a>' for i, label in enumerate(labels))
    return f'<nav class="bottom-nav" aria-label="Mobile" {data_attrs(c)} style="{style_attr(c)}">{items}</nav>'


def render_metric_card(c: dict) -> str:
    return f'''<section class="metric-card" {data_attrs(c)} style="{style_attr(c)}">
  <span class="metric-label">{esc(c.get("label", ""))}</span>
  <strong class="metric-value">{esc(c.get("value", ""))}</strong>
  <span class="metric-trend">{esc(c.get("trend", ""))}</span>
</section>'''


def chart_points(values: list[int]) -> str:
    if not values:
        values = [0]
    max_v = max(values)
    min_v = min(values)
    spread = max(1, max_v - min_v)
    points = []
    for index, value in enumerate(values):
        x = 8 + index * (284 / max(1, len(values) - 1))
        y = 118 - ((value - min_v) / spread) * 92
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


def render_chart_card(c: dict) -> str:
    points = chart_points(c.get("values", []))
    return f'''<section class="chart-card" {data_attrs(c)} style="{style_attr(c)}">
  <h2>{esc(c.get("title", "Trend"))}</h2>
  <svg class="chart" viewBox="0 0 300 136" role="img" aria-label="{esc(c.get("title", "Trend"))}">
    <polyline points="{points}" />
  </svg>
</section>'''


def render_search(c: dict) -> str:
    return f'''<label class="search" {data_attrs(c)} style="{style_attr(c)}">
  <span class="search-icon" aria-hidden="true"></span>
  <input type="search" placeholder="{esc(c.get("placeholder", "Search"))}">
</label>'''


def render_list_row(c: dict) -> str:
    return f'''<article class="list-row" {data_attrs(c)} style="{style_attr(c)}">
  <span class="row-icon" aria-hidden="true"></span>
  <strong>{esc(c.get("title", ""))}</strong>
  <p>{esc(c.get("detail", ""))}</p>
</article>'''


def render_inspector(c: dict) -> str:
    return f'''<section class="inspector" {data_attrs(c)} style="{style_attr(c)}">
  <h2>{esc(c.get("title", ""))}</h2>
  <p>{esc(c.get("body", ""))}</p>
  <code>"components[0].text": "..."</code>
</section>'''


def render_toggle_row(c: dict) -> str:
    checked = " checked" if c.get("enabled") else ""
    return f'''<label class="toggle-row" {data_attrs(c)} style="{style_attr(c)}">
  <span>{esc(c.get("title", ""))}</span>
  <input type="checkbox"{checked}>
</label>'''


def render_component(c: dict) -> str:
    renderers = {
        "text": render_text,
        "button": render_button,
        "sidebar": render_sidebar,
        "nav_item": render_nav_item,
        "bottom_nav": render_bottom_nav,
        "metric_card": render_metric_card,
        "chart_card": render_chart_card,
        "search": render_search,
        "list_row": render_list_row,
        "inspector": render_inspector,
        "toggle_row": render_toggle_row,
    }
    renderer = renderers.get(c["type"])
    if renderer:
        return renderer(c)
    return f'<div class="component component-{esc(c["type"])}" {data_attrs(c)} style="{style_attr(c)}"></div>'


def render_frame(frame: dict) -> str:
    components = "\n".join(render_component(component) for component in frame.get("components", []))
    return f'''<section class="screen-frame" data-frame-id="{esc(frame["id"])}" style="width:{frame["w"]}px;height:{frame["h"]}px">
  <div class="frame-label">{esc(frame["name"])}</div>
  {components}
</section>'''


def render_html(spec: dict) -> str:
    colors = spec["tokens"]["colors"]
    frames = "\n".join(render_frame(frame) for frame in spec.get("frames", []))
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(spec.get("name", "Lunacy Design"))}</title>
  <style>
:root {{
{css_vars(colors)}
  --font-ui: Inter, Arial, sans-serif;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: #dfe5ee;
  color: var(--color-text);
  font-family: var(--font-ui);
}}
.topbar {{
  position: sticky;
  top: 0;
  z-index: 10;
  padding: 16px 24px;
  background: #ffffff;
  border-bottom: 1px solid #cbd5e1;
}}
.canvas {{
  display: flex;
  gap: 80px;
  align-items: flex-start;
  min-width: max-content;
  padding: 72px 80px;
}}
.screen-frame {{
  position: relative;
  flex: 0 0 auto;
  overflow: hidden;
  background: var(--color-canvas);
  border-radius: 18px;
  box-shadow: 0 24px 70px rgba(23, 32, 51, .18);
}}
.frame-label {{
  position: absolute;
  left: 0;
  top: -34px;
  color: #172033;
  font-size: 18px;
  font-weight: 800;
}}
.text {{ margin: 0; line-height: 1.22; overflow: hidden; }}
.text-eyebrow {{ color: var(--color-primary); font-size: 12px; font-weight: 800; letter-spacing: 0; }}
.text-headline {{ color: var(--color-text); font-weight: 800; }}
.text-body {{ color: var(--color-muted); }}
.sidebar, .metric-card, .chart-card, .list-row, .search, .toggle-row {{
  background: var(--color-surface);
  border: 1px solid var(--color-line);
  border-radius: 8px;
}}
.sidebar {{ border-radius: 12px; }}
.nav-item {{
  display: flex;
  align-items: center;
  padding: 0 14px;
  border-radius: 8px;
  color: var(--color-muted);
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
}}
.nav-item.is-active {{ background: var(--color-surface-alt); color: var(--color-text); }}
.bottom-nav {{
  display: grid;
  grid-auto-flow: column;
  align-items: center;
  border-radius: 18px;
}}
.bottom-nav-item {{
  display: flex;
  align-items: end;
  justify-content: center;
  height: 100%;
  padding-bottom: 10px;
  color: var(--color-muted);
  font-size: 11px;
  font-weight: 700;
  text-decoration: none;
}}
.bottom-nav-item.is-active {{ color: var(--color-primary); }}
.button {{
  border: 0;
  border-radius: 8px;
  background: var(--color-primary);
  color: #fff;
  font: 700 14px var(--font-ui);
}}
.metric-card {{ padding: 18px 20px; }}
.metric-label, .metric-trend {{ display: block; font-size: 13px; font-weight: 700; }}
.metric-label {{ color: var(--color-muted); }}
.metric-value {{ display: block; margin-top: 8px; color: var(--color-text); font-size: 30px; }}
.metric-trend {{ position: absolute; right: 20px; bottom: 18px; color: var(--color-success); }}
.chart-card {{ padding: 18px 20px; }}
.chart-card h2, .inspector h2 {{ margin: 0; font-size: 17px; }}
.chart {{ width: 100%; height: calc(100% - 38px); margin-top: 12px; }}
.chart polyline {{ fill: none; stroke: var(--color-primary); stroke-width: 5; stroke-linecap: round; stroke-linejoin: round; }}
.search {{ display: flex; align-items: center; gap: 14px; padding: 0 16px; }}
.search-icon {{ width: 16px; height: 16px; border: 2px solid var(--color-muted); border-radius: 50%; }}
.search input {{ width: 100%; border: 0; outline: 0; background: transparent; color: var(--color-text); font: 500 14px var(--font-ui); }}
.list-row {{ padding: 14px 16px 14px 68px; }}
.row-icon {{ position: absolute; left: 16px; top: 18px; width: 36px; height: 36px; background: var(--color-surface-alt); border-radius: 8px; }}
.list-row strong {{ display: block; font-size: 16px; }}
.list-row p {{ margin: 6px 0 0; color: var(--color-muted); font-size: 13px; }}
.inspector {{ padding: 20px; background: var(--color-surface-alt); border: 1px solid var(--color-line); border-radius: 10px; }}
.inspector p {{ color: var(--color-muted); }}
.inspector code {{ display: block; padding: 16px; background: var(--color-surface); border: 1px solid var(--color-line); border-radius: 8px; color: var(--color-muted); }}
.toggle-row {{ display: flex; align-items: center; justify-content: space-between; padding: 0 18px; font-weight: 700; }}
.toggle-row input {{ width: 48px; height: 26px; accent-color: var(--color-primary); }}
  </style>
</head>
<body>
  <header class="topbar"><strong>{esc(spec.get("name", "Lunacy Design"))}</strong></header>
  <main class="canvas">
{frames}
  </main>
</body>
</html>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output", required=True)
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
    output.write_text(render_html(spec), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
