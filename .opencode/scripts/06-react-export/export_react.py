#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def js(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)


def expr(value: object) -> str:
    return "{" + js(value) + "}"


def pascal(value: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", value)
    return "".join(part[:1].upper() + part[1:] for part in parts if part) or "GeneratedDesign"


def style_obj(component: dict, extra: dict | None = None) -> str:
    style = {
        "position": "absolute",
        "left": component["x"],
        "top": component["y"],
        "width": component["w"],
        "height": component["h"],
    }
    if extra:
        style.update(extra)
    return "{{ " + ", ".join(f"{key}: {js(value)}" for key, value in style.items()) + " }}"


def data_attrs(component: dict) -> str:
    return f'data-layer-id={{{js(component["id"])}}} data-component-type={{{js(component["type"])}}}'


def icon(name: str | None) -> str:
    return f'<span aria-hidden className="inline-block h-4 w-4 rounded border-2 border-current {("bg-current" if name == "spark" else "")}" />'


def text_component(c: dict) -> str:
    role = c.get("role", "body")
    tag = "h1" if role == "headline" else "p"
    cls = {
        "headline": "m-0 overflow-hidden font-extrabold leading-tight text-[var(--color-text)]",
        "eyebrow": "m-0 overflow-hidden text-xs font-extrabold uppercase text-[var(--color-primary)]",
        "body": "m-0 overflow-hidden leading-snug text-[var(--color-muted)]",
        "brand": "m-0 overflow-hidden font-bold text-[var(--color-text)]",
    }.get(role, "m-0 overflow-hidden text-[var(--color-text)]")
    size = c.get("size")
    style = style_obj(c, {"fontSize": size} if size else None)
    return f'<{tag} className="{cls}" {data_attrs(c)} style={style}>{expr(c.get("text", ""))}</{tag}>'


def button_component(c: dict) -> str:
    content = f'{icon(c.get("icon"))}<span>{expr(c.get("text", "Button"))}</span>' if c.get("icon") else expr(c.get("text", "Button"))
    return f'<button className="inline-flex items-center justify-center gap-2 rounded-lg bg-[var(--color-primary)] text-sm font-bold text-white" {data_attrs(c)} style={style_obj(c)}>{content}</button>'


def card_component(c: dict) -> str:
    return f'''<section className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] p-5" {data_attrs(c)} style={style_obj(c)}>
  <span className="text-sm font-bold text-[var(--color-muted)]">{expr(c.get("label", ""))}</span>
  <strong className="mt-2 block text-3xl font-extrabold text-[var(--color-text)]">{expr(c.get("value", ""))}</strong>
  <span className="absolute bottom-5 right-5 text-sm font-bold text-[var(--color-success)]">{expr(c.get("trend", ""))}</span>
</section>'''


def chart_component(c: dict) -> str:
    values = c.get("values", [])
    max_v = max(values) if values else 1
    min_v = min(values) if values else 0
    spread = max(1, max_v - min_v)
    points = []
    for index, value in enumerate(values or [0]):
        x = 8 + index * (284 / max(1, len(values or [0]) - 1))
        y = 118 - ((value - min_v) / spread) * 92
        points.append(f"{x:.1f},{y:.1f}")
    return f'''<section className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] p-5" {data_attrs(c)} style={style_obj(c)}>
  <h2 className="m-0 text-base font-bold text-[var(--color-text)]">{expr(c.get("title", "Trend"))}</h2>
  <svg className="mt-3 h-[calc(100%-38px)] w-full" viewBox="0 0 300 136" role="img">
    <polyline points={js(" ".join(points))} fill="none" stroke="var(--color-primary)" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
</section>'''


def list_component(c: dict) -> str:
    return f'''<article className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] py-3 pl-16 pr-4" {data_attrs(c)} style={style_obj(c)}>
  <span className="absolute left-4 top-4 h-9 w-9 rounded-lg bg-[var(--color-surface-alt)]" />
  <strong className="block text-base text-[var(--color-text)]">{expr(c.get("title", ""))}</strong>
  <p className="m-0 mt-1 text-xs text-[var(--color-muted)]">{expr(c.get("detail", ""))}</p>
</article>'''


def simple_component(c: dict) -> str:
    kind = c["type"]
    if kind == "sidebar":
        return f'<nav className="rounded-xl border border-[var(--color-line)] bg-[var(--color-surface)]" aria-label="Primary" {data_attrs(c)} style={style_obj(c)} />'
    if kind == "nav_item":
        active = " bg-[var(--color-surface-alt)] text-[var(--color-text)]" if c.get("active") else " text-[var(--color-muted)]"
        return f'<a href="#" className="flex items-center gap-3 rounded-lg px-4 text-sm font-bold{active}" {data_attrs(c)} style={style_obj(c)}>{icon(c.get("icon"))}<span>{expr(c.get("text", "Item"))}</span></a>'
    if kind == "bottom_nav":
        labels = c.get("labels", [])
        items = "".join(f'<a href="#" className="grid place-items-center text-xs font-bold {"text-[var(--color-primary)]" if i == 0 else "text-[var(--color-muted)]"}">{expr(label)}</a>' for i, label in enumerate(labels))
        return f'<nav className="grid grid-flow-col rounded-2xl border border-[var(--color-line)] bg-[var(--color-surface)]" {data_attrs(c)} style={style_obj(c)}>{items}</nav>'
    if kind == "search":
        return f'<label className="flex items-center gap-3 rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] px-4" {data_attrs(c)} style={style_obj(c)}>{icon("search")}<input className="w-full bg-transparent text-sm outline-none" type="search" placeholder={js(c.get("placeholder", "Search"))} /></label>'
    if kind == "tabs":
        labels = c.get("labels", [])
        buttons = "".join(f'<button className="rounded-md px-3 text-sm font-bold {"bg-[var(--color-surface-alt)] text-[var(--color-text)]" if i == c.get("active", 0) else "text-[var(--color-muted)]"}">{expr(label)}</button>' for i, label in enumerate(labels))
        return f'<div className="grid grid-flow-col gap-1 rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] p-1" role="tablist" {data_attrs(c)} style={style_obj(c)}>{buttons}</div>'
    if kind == "toggle_row":
        checked = "defaultChecked" if c.get("enabled") else ""
        return f'<label className="flex items-center justify-between rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] px-5 font-bold" {data_attrs(c)} style={style_obj(c)}><span>{js(c.get("title", ""))}</span><input type="checkbox" {checked} /></label>'
    if kind == "dropdown":
        return f'<label className="grid rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] px-4 py-2" {data_attrs(c)} style={style_obj(c)}><span className="text-xs font-bold text-[var(--color-muted)]">{expr(c.get("label", "Select"))}</span><select className="bg-transparent font-bold"><option>{expr(c.get("value", "Option"))}</option></select></label>'
    if kind == "toast":
        return f'<aside className="rounded-lg border border-[var(--color-line)] border-l-[6px] border-l-[var(--color-success)] bg-[var(--color-surface)] px-4 py-2" {data_attrs(c)} style={style_obj(c)}><strong>{expr(c.get("title", ""))}</strong><span className="block text-xs text-[var(--color-muted)]">{expr(c.get("detail", ""))}</span></aside>'
    return f'<div className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)]" {data_attrs(c)} style={style_obj(c)} />'


def rich_component(c: dict) -> str:
    kind = c["type"]
    if kind == "table":
        columns = "".join(f"<th>{column}</th>" for column in c.get("columns", []))
        rows = "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in c.get("rows", []))
        return f'<section className="overflow-hidden rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] text-sm" {data_attrs(c)} style={style_obj(c)}><table className="w-full"><thead><tr>{columns}</tr></thead><tbody>{rows}</tbody></table></section>'
    if kind == "form":
        fields = "".join(f'<label className="grid gap-1 text-xs font-bold text-[var(--color-muted)]"><span>{field}</span><input className="h-10 rounded-md border border-[var(--color-line)] bg-[var(--color-surface-alt)]" /></label>' for field in c.get("fields", []))
        return f'<form className="grid gap-3 rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] p-5" {data_attrs(c)} style={style_obj(c)}><h2 className="m-0 font-bold">{expr(c.get("title", "Form"))}</h2>{fields}<button type="button" className="h-10 rounded-lg bg-[var(--color-primary)] font-bold text-white">{expr(c.get("action", "Submit"))}</button></form>'
    if kind == "modal":
        actions = "".join(f'<button className="h-10 rounded-lg px-4 font-bold {"bg-[var(--color-primary)] text-white" if i == len(c.get("actions", [])) - 1 else "bg-[var(--color-surface-alt)]"}">{action}</button>' for i, action in enumerate(c.get("actions", [])))
        return f'<section role="dialog" className="rounded-xl border border-[var(--color-line)] bg-[var(--color-surface)] p-5 shadow-xl" {data_attrs(c)} style={style_obj(c)}><h2 className="m-0 font-bold">{expr(c.get("title", "Modal"))}</h2><p className="text-sm text-[var(--color-muted)]">{expr(c.get("body", ""))}</p><div className="absolute bottom-5 right-5 flex gap-2">{actions}</div></section>'
    if kind == "kanban":
        cols = []
        for col in c.get("columns", []):
            items = "".join(f'<li className="rounded-md border border-[var(--color-line)] bg-[var(--color-surface)] p-2 text-xs font-bold">{item}</li>' for item in col.get("items", []))
            cols.append(f'<section className="rounded-lg bg-[var(--color-surface-alt)] p-3"><h3 className="m-0 mb-2 text-sm">{col.get("title", "Column")}</h3><ul className="grid gap-2 p-0">{items}</ul></section>')
        return f'<div className="grid grid-flow-col gap-3 rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] p-3" {data_attrs(c)} style={style_obj(c)}>{"".join(cols)}</div>'
    if kind == "pricing_card":
        features = "".join(f'<li>{feature}</li>' for feature in c.get("features", []))
        return f'<section className="rounded-lg border border-[var(--color-line)] bg-[var(--color-surface)] p-5" {data_attrs(c)} style={style_obj(c)}><h2>{expr(c.get("title", "Plan"))}</h2><strong className="text-3xl text-[var(--color-primary)]">{expr(c.get("price", "$0"))}</strong><ul>{features}</ul></section>'
    return simple_component(c)


def component(c: dict) -> str:
    if c["type"] == "text":
        return text_component(c)
    if c["type"] == "button":
        return button_component(c)
    if c["type"] == "metric_card":
        return card_component(c)
    if c["type"] == "chart_card":
        return chart_component(c)
    if c["type"] == "list_row":
        return list_component(c)
    if c["type"] in {"table", "form", "modal", "kanban", "pricing_card"}:
        return rich_component(c)
    return simple_component(c)


def frame(frame_data: dict) -> str:
    children = "\n      ".join(component(item) for item in frame_data.get("components", []))
    return f'''<section className="relative shrink-0 overflow-hidden rounded-[18px] bg-[var(--color-canvas)] shadow-2xl" data-frame-id={js(frame_data["id"])} style={{{{ width: {frame_data["w"]}, height: {frame_data["h"]} }}}}>
      <div className="absolute -top-9 left-0 text-lg font-extrabold text-slate-900">{expr(frame_data["name"])}</div>
      {children}
    </section>'''


def render(spec: dict, component_name: str) -> str:
    colors = spec["tokens"]["colors"]
    vars_code = "\n    ".join(f"'--color-{key.replace('_', '-')}': {js(value)}," for key, value in colors.items())
    frames = "\n    ".join(frame(item) for item in spec.get("frames", []))
    return f'''import React from "react";

export default function {component_name}() {{
  const tokens = {{
    {vars_code}
  }} as React.CSSProperties;

  return (
    <main className="min-h-screen overflow-auto bg-slate-200 p-20 font-sans" style={{tokens}}>
      <header className="mb-8">
        <h1 className="m-0 text-2xl font-extrabold text-slate-900">{expr(spec.get("name", "Lunacy Design"))}</h1>
        <p className="m-0 mt-1 text-sm font-semibold text-slate-600">Preset: {expr(spec.get("design_preset", "custom"))}</p>
      </header>
      <div className="flex min-w-max items-start gap-20">
    {frames}
      </div>
    </main>
  );
}}
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--component-name")
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
    name = args.component_name or pascal(spec.get("name", "LunacyDesign"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(spec, name), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
