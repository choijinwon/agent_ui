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
    return "\n".join(f"  --color-{name.replace('_', '-')}: {value};" for name, value in colors.items())


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


def icon(name: str | None) -> str:
    label = esc(name or "asset")
    return f'<span class="icon icon-{label}" aria-hidden="true"></span>'


def render_text(c: dict) -> str:
    role = c.get("role", "body")
    tag = "h1" if role == "headline" else "p"
    cls = f"text text-{role}"
    return f'<{tag} class="{cls}" {data_attrs(c)} style="{style_attr(c)}">{esc(c.get("text", ""))}</{tag}>'


def render_button(c: dict) -> str:
    content = f'{icon(c.get("icon"))}<span>{esc(c.get("text", "Button"))}</span>' if c.get("icon") else esc(c.get("text", "Button"))
    return f'<button class="button button-{esc(c.get("tone", "default"))}" {data_attrs(c)} style="{style_attr(c)}">{content}</button>'


def render_sidebar(c: dict) -> str:
    return f'<nav class="sidebar" aria-label="Primary" {data_attrs(c)} style="{style_attr(c)}"></nav>'


def render_nav_item(c: dict) -> str:
    active = " is-active" if c.get("active") else ""
    return f'<a class="nav-item{active}" href="#" {data_attrs(c)} style="{style_attr(c)}">{icon(c.get("icon"))}<span>{esc(c.get("text", "Item"))}</span></a>'


def render_bottom_nav(c: dict) -> str:
    labels = c.get("labels", [])
    icons = c.get("icons", [])
    items = "".join(
        f'<a href="#" class="bottom-nav-item{" is-active" if i == 0 else ""}">{icon(icons[i] if i < len(icons) else None)}<span>{esc(label)}</span></a>'
        for i, label in enumerate(labels)
    )
    return f'<nav class="bottom-nav" aria-label="Mobile" {data_attrs(c)} style="{style_attr(c)}">{items}</nav>'


def render_metric_card(c: dict) -> str:
    return f'''<section class="metric-card" {data_attrs(c)} style="{style_attr(c)}">
  <span class="metric-icon">{icon(c.get("icon"))}</span>
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
  {icon("search")}
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


def render_tabs(c: dict) -> str:
    labels = c.get("labels", [])
    active = int(c.get("active", 0))
    buttons = "".join(f'<button class="{"is-active" if i == active else ""}">{esc(label)}</button>' for i, label in enumerate(labels))
    return f'<div class="tabs" role="tablist" {data_attrs(c)} style="{style_attr(c)}">{buttons}</div>'


def render_dropdown(c: dict) -> str:
    options = "".join(f'<option{" selected" if opt == c.get("value") else ""}>{esc(opt)}</option>' for opt in c.get("options", []))
    return f'''<label class="dropdown" {data_attrs(c)} style="{style_attr(c)}">
  <span>{esc(c.get("label", "Select"))}</span>
  <select>{options}</select>
</label>'''


def render_table(c: dict) -> str:
    cols = "".join(f'<th>{esc(col)}</th>' for col in c.get("columns", []))
    rows = "".join("<tr>" + "".join(f"<td>{esc(cell)}</td>" for cell in row) + "</tr>" for row in c.get("rows", []))
    return f'''<section class="table-card" {data_attrs(c)} style="{style_attr(c)}">
  <table><thead><tr>{cols}</tr></thead><tbody>{rows}</tbody></table>
</section>'''


def render_form(c: dict) -> str:
    fields = "".join(f'<label><span>{esc(field)}</span><input placeholder="{esc(field)}"></label>' for field in c.get("fields", []))
    return f'''<form class="form-card" {data_attrs(c)} style="{style_attr(c)}">
  <h2>{esc(c.get("title", "Form"))}</h2>
  {fields}
  <button type="button">{esc(c.get("action", "Submit"))}</button>
</form>'''


def render_modal(c: dict) -> str:
    actions = "".join(f'<button class="{"primary" if i == len(c.get("actions", [])) - 1 else ""}">{esc(action)}</button>' for i, action in enumerate(c.get("actions", [])))
    return f'''<section class="modal" role="dialog" {data_attrs(c)} style="{style_attr(c)}">
  <h2>{esc(c.get("title", "Modal"))}</h2>
  <p>{esc(c.get("body", ""))}</p>
  <div class="modal-actions">{actions}</div>
</section>'''


def render_toast(c: dict) -> str:
    return f'''<aside class="toast toast-{esc(c.get("tone", "success"))}" {data_attrs(c)} style="{style_attr(c)}">
  <strong>{esc(c.get("title", "Notice"))}</strong>
  <span>{esc(c.get("detail", ""))}</span>
</aside>'''


def render_pricing_card(c: dict) -> str:
    features = "".join(f'<li>{esc(feature)}</li>' for feature in c.get("features", []))
    return f'''<section class="pricing-card" {data_attrs(c)} style="{style_attr(c)}">
  <h2>{esc(c.get("title", "Plan"))}</h2>
  <strong>{esc(c.get("price", "$0"))}</strong>
  <ul>{features}</ul>
</section>'''


def render_calendar(c: dict) -> str:
    selected = set(c.get("selected", []))
    days = "".join(f'<span class="{"is-selected" if day in selected else ""}">{day}</span>' for day in range(1, 29))
    return f'''<section class="calendar" {data_attrs(c)} style="{style_attr(c)}">
  <h2>{esc(c.get("title", "Calendar"))}</h2>
  <div>{days}</div>
</section>'''


def render_kanban(c: dict) -> str:
    columns = []
    for column in c.get("columns", []):
        items = "".join(f'<li>{esc(item)}</li>' for item in column.get("items", []))
        columns.append(f'<section><h3>{esc(column.get("title", "Column"))}</h3><ul>{items}</ul></section>')
    return f'<div class="kanban" {data_attrs(c)} style="{style_attr(c)}">{"".join(columns)}</div>'


def render_image_placeholder(c: dict) -> str:
    return f'<figure class="image-placeholder" {data_attrs(c)} style="{style_attr(c)}"><figcaption>{esc(c.get("label", "Image asset"))}</figcaption></figure>'


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
body {{ margin: 0; background: #dfe5ee; color: var(--color-text); font-family: var(--font-ui); }}
.topbar {{ position: sticky; top: 0; z-index: 10; padding: 16px 24px; background: #fff; border-bottom: 1px solid #cbd5e1; }}
.canvas {{ display: flex; gap: 80px; align-items: flex-start; min-width: max-content; padding: 72px 80px; }}
.screen-frame {{ position: relative; flex: 0 0 auto; overflow: hidden; background: var(--color-canvas); border-radius: 18px; box-shadow: 0 24px 70px rgba(23,32,51,.18); }}
.frame-label {{ position: absolute; left: 0; top: -34px; color: #172033; font-size: 18px; font-weight: 800; }}
.text {{ margin: 0; line-height: 1.22; overflow: hidden; }}
.text-eyebrow {{ color: var(--color-primary); font-size: 12px; font-weight: 800; letter-spacing: 0; }}
.text-headline {{ color: var(--color-text); font-weight: 800; }}
.text-body {{ color: var(--color-muted); }}
.icon {{ display: inline-block; width: 16px; height: 16px; border: 2px solid currentColor; border-radius: 5px; }}
.icon-chart {{ border-radius: 50%; border-left-color: transparent; }}
.icon-spark {{ border-radius: 50%; background: currentColor; border: 0; }}
.sidebar, .metric-card, .chart-card, .list-row, .search, .toggle-row, .tabs, .dropdown, .table-card, .form-card, .modal, .toast, .pricing-card, .calendar, .kanban, .image-placeholder {{
  background: var(--color-surface); border: 1px solid var(--color-line); border-radius: 8px;
}}
.sidebar {{ border-radius: 12px; }}
.nav-item {{ display: flex; align-items: center; gap: 12px; padding: 0 14px; border-radius: 8px; color: var(--color-muted); font-size: 14px; font-weight: 700; text-decoration: none; }}
.nav-item.is-active {{ background: var(--color-surface-alt); color: var(--color-text); }}
.bottom-nav {{ display: grid; grid-auto-flow: column; align-items: center; border-radius: 18px; }}
.bottom-nav-item {{ display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; height: 100%; color: var(--color-muted); font-size: 11px; font-weight: 700; text-decoration: none; }}
.bottom-nav-item.is-active {{ color: var(--color-primary); }}
.button {{ display: inline-flex; align-items: center; justify-content: center; gap: 8px; border: 0; border-radius: 8px; background: var(--color-primary); color: #fff; font: 700 14px var(--font-ui); }}
.metric-card {{ padding: 18px 20px; }}
.metric-icon {{ position: absolute; right: 20px; top: 18px; display: grid; place-items: center; width: 36px; height: 36px; color: var(--color-primary); background: var(--color-surface-alt); border-radius: 8px; }}
.metric-label, .metric-trend {{ display: block; font-size: 13px; font-weight: 700; }}
.metric-label {{ color: var(--color-muted); }}
.metric-value {{ display: block; margin-top: 8px; color: var(--color-text); font-size: 30px; }}
.metric-trend {{ position: absolute; right: 20px; bottom: 18px; color: var(--color-success); }}
.chart-card {{ padding: 18px 20px; }}
.chart-card h2, .inspector h2, .form-card h2, .calendar h2, .modal h2, .pricing-card h2 {{ margin: 0; font-size: 17px; }}
.chart {{ width: 100%; height: calc(100% - 38px); margin-top: 12px; }}
.chart polyline {{ fill: none; stroke: var(--color-primary); stroke-width: 5; stroke-linecap: round; stroke-linejoin: round; }}
.search {{ display: flex; align-items: center; gap: 14px; padding: 0 16px; color: var(--color-muted); }}
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
.tabs {{ display: grid; grid-auto-flow: column; gap: 4px; padding: 4px; }}
.tabs button {{ border: 0; border-radius: 6px; background: transparent; color: var(--color-muted); font: 700 13px var(--font-ui); }}
.tabs button.is-active {{ background: var(--color-surface-alt); color: var(--color-text); }}
.dropdown {{ display: grid; gap: 4px; padding: 8px 14px; }}
.dropdown span {{ color: var(--color-muted); font-size: 11px; font-weight: 800; }}
.dropdown select {{ border: 0; outline: 0; background: transparent; color: var(--color-text); font: 700 15px var(--font-ui); }}
.table-card {{ overflow: hidden; }}
.table-card table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
.table-card th {{ height: 48px; background: var(--color-surface-alt); color: var(--color-muted); text-align: left; }}
.table-card th, .table-card td {{ padding: 0 16px; border-bottom: 1px solid var(--color-line); }}
.table-card td {{ height: 44px; font-weight: 600; }}
.form-card {{ display: grid; gap: 12px; padding: 18px; }}
.form-card label {{ display: grid; gap: 6px; color: var(--color-muted); font-size: 12px; font-weight: 800; }}
.form-card input {{ height: 40px; border: 1px solid var(--color-line); border-radius: 6px; background: var(--color-surface-alt); }}
.form-card button, .modal button {{ height: 40px; border: 0; border-radius: 8px; background: var(--color-primary); color: #fff; font-weight: 800; }}
.modal {{ padding: 20px; box-shadow: 0 20px 48px rgba(23,32,51,.18); }}
.modal p {{ color: var(--color-muted); }}
.modal-actions {{ position: absolute; right: 20px; bottom: 20px; display: flex; gap: 10px; }}
.modal-actions button:not(.primary) {{ background: var(--color-surface-alt); color: var(--color-text); }}
.toast {{ padding: 10px 16px 10px 20px; border-left: 5px solid var(--color-success); }}
.toast strong, .toast span {{ display: block; }}
.toast span {{ margin-top: 3px; color: var(--color-muted); font-size: 12px; }}
.pricing-card {{ padding: 18px 20px; }}
.pricing-card strong {{ display: block; margin-top: 8px; color: var(--color-primary); font-size: 34px; }}
.pricing-card ul {{ margin: 14px 0 0; padding-left: 18px; font-size: 13px; }}
.calendar {{ padding: 18px; }}
.calendar div {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-top: 18px; }}
.calendar span {{ display: grid; place-items: center; height: 34px; background: var(--color-surface-alt); border-radius: 6px; font-size: 12px; font-weight: 700; }}
.calendar span.is-selected {{ background: var(--color-primary); color: #fff; }}
.kanban {{ display: grid; grid-auto-flow: column; gap: 12px; padding: 12px; }}
.kanban section {{ min-width: 0; padding: 12px; background: var(--color-surface-alt); border-radius: 8px; }}
.kanban h3 {{ margin: 0 0 10px; font-size: 14px; }}
.kanban ul {{ display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }}
.kanban li {{ padding: 10px; background: var(--color-surface); border: 1px solid var(--color-line); border-radius: 6px; font-size: 12px; font-weight: 700; }}
.image-placeholder {{ display: grid; place-items: end start; padding: 16px; background: linear-gradient(135deg, var(--color-surface-alt), var(--color-surface)); color: var(--color-muted); }}
  </style>
</head>
<body>
  <header class="topbar"><strong>{esc(spec.get("name", "Lunacy Design"))}</strong> <span>Preset: {esc(spec.get("design_preset", "custom"))}</span></header>
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
