#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


PRESETS = {
    "saas": {
        "colors": {
            "canvas": "#F5F7FA",
            "surface": "#FFFFFF",
            "surface_alt": "#EEF2F7",
            "text": "#172033",
            "muted": "#5B667A",
            "primary": "#2563EB",
            "secondary": "#14B8A6",
            "success": "#16A34A",
            "danger": "#DC2626",
            "warning": "#D97706",
            "line": "#D7DEE8",
        },
        "radius": {"sm": 6, "md": 8, "lg": 12},
        "density": "balanced",
    },
    "fintech": {
        "colors": {
            "canvas": "#F7FAFC",
            "surface": "#FFFFFF",
            "surface_alt": "#E8F3F1",
            "text": "#10201D",
            "muted": "#51645F",
            "primary": "#087F5B",
            "secondary": "#0EA5A4",
            "success": "#16A34A",
            "danger": "#B42318",
            "warning": "#B7791F",
            "line": "#D7E5E1",
        },
        "radius": {"sm": 6, "md": 8, "lg": 10},
        "density": "dense",
    },
    "mobile-native": {
        "colors": {
            "canvas": "#FAFAFB",
            "surface": "#FFFFFF",
            "surface_alt": "#F0F2F5",
            "text": "#111827",
            "muted": "#6B7280",
            "primary": "#4F46E5",
            "secondary": "#06B6D4",
            "success": "#22C55E",
            "danger": "#EF4444",
            "warning": "#F59E0B",
            "line": "#E5E7EB",
        },
        "radius": {"sm": 8, "md": 12, "lg": 18},
        "density": "comfortable",
    },
    "ecommerce": {
        "colors": {
            "canvas": "#FBFAF8",
            "surface": "#FFFFFF",
            "surface_alt": "#F3EEE7",
            "text": "#211A16",
            "muted": "#6D625B",
            "primary": "#C2410C",
            "secondary": "#0F766E",
            "success": "#15803D",
            "danger": "#BE123C",
            "warning": "#D97706",
            "line": "#E5DDD3",
        },
        "radius": {"sm": 4, "md": 8, "lg": 10},
        "density": "balanced",
    },
    "admin": {
        "colors": {
            "canvas": "#F3F4F6",
            "surface": "#FFFFFF",
            "surface_alt": "#E5E7EB",
            "text": "#111827",
            "muted": "#4B5563",
            "primary": "#1D4ED8",
            "secondary": "#7C3AED",
            "success": "#047857",
            "danger": "#B91C1C",
            "warning": "#B45309",
            "line": "#D1D5DB",
        },
        "radius": {"sm": 4, "md": 6, "lg": 8},
        "density": "dense",
    },
    "dark": {
        "colors": {
            "canvas": "#0B1020",
            "surface": "#151B2E",
            "surface_alt": "#202842",
            "text": "#F5F7FB",
            "muted": "#A8B0C4",
            "primary": "#56CCF2",
            "secondary": "#F2C94C",
            "success": "#6FCF97",
            "danger": "#EB5757",
            "warning": "#F2C94C",
            "line": "#313A56",
        },
        "radius": {"sm": 6, "md": 8, "lg": 12},
        "density": "balanced",
    },
}


def slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-") or "screen"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def frame_size(platform: str) -> tuple[int, int]:
    if platform == "mobile":
        return 390, 844
    if platform == "tablet":
        return 834, 1112
    return 1440, 1024


def pick_preset(brief: dict, requested: str | None) -> str:
    if requested:
        return requested
    styles = set(brief.get("style", []))
    source = brief.get("source_brief", "").lower()
    product = brief.get("product", "").lower()
    if "dark" in styles:
        return "dark"
    if any(word in source or word in product for word in ["finance", "bank", "payment", "spending", "budget"]):
        return "fintech"
    if any(word in source or word in product for word in ["shop", "commerce", "product", "cart"]):
        return "ecommerce"
    if any(word in source or word in product for word in ["admin", "ops", "operations", "table"]):
        return "admin"
    if brief.get("platform") == "mobile":
        return "mobile-native"
    return "saas"


def component(kind: str, cid: str, x: int, y: int, w: int, h: int, **extra) -> dict:
    data = {"id": cid, "type": kind, "x": x, "y": y, "w": w, "h": h}
    data.update(extra)
    return data


def asset_manifest(preset: str) -> dict:
    return {
        "asset_dir": "assets",
        "icons": {
            "home": "inline",
            "chart": "inline",
            "wallet": "inline",
            "settings": "inline",
            "spark": "inline",
            "search": "inline",
        },
        "image_placeholders": [
            {"id": "hero-product", "kind": "product", "recommended_size": "640x420"},
            {"id": "avatar-user", "kind": "avatar", "recommended_size": "160x160"},
        ],
        "preset": preset,
    }


def nav_components(width: int, height: int, platform: str, colors: dict, prefix: str) -> list[dict]:
    if platform == "mobile":
        return [
            component("bottom_nav", f"{prefix}-bottom-nav", 16, height - 84, width - 32, 64,
                      labels=["Home", "Insights", "Cards", "Settings"], icons=["home", "chart", "wallet", "settings"],
                      fill=colors["surface"]),
        ]
    return [
        component("sidebar", f"{prefix}-sidebar", 24, 24, 248, height - 48, fill=colors["surface"]),
        component("text", f"{prefix}-brand-title", 48, 52, 180, 28, text="Lunacy Agent", role="brand", size=20, weight=700),
        component("nav_item", f"{prefix}-nav-overview", 48, 120, 176, 40, text="Overview", icon="home", active=True),
        component("nav_item", f"{prefix}-nav-designs", 48, 168, 176, 40, text="Designs", icon="chart", active=False),
        component("nav_item", f"{prefix}-nav-settings", 48, 216, 176, 40, text="Settings", icon="settings", active=False),
    ]


def overview_frame(name: str, index: int, brief: dict, width: int, height: int, colors: dict, preset: str) -> dict:
    platform = brief["platform"]
    prefix = slug(name)
    margin = 24 if platform == "mobile" else 312
    top = 40 if platform == "mobile" else 56
    content_w = width - 48 if platform == "mobile" else width - margin - 56
    title = f"{brief['product'].title()} {name.title()}"
    comps = nav_components(width, height, platform, colors, prefix)
    comps.extend([
        component("text", f"{prefix}-eyebrow", margin, top, content_w, 20,
                  text=brief["audience"].upper(), role="eyebrow", size=12, weight=700),
        component("text", f"{prefix}-title", margin, top + 28, content_w, 54,
                  text=title, role="headline", size=34 if platform != "mobile" else 28, weight=800),
        component("text", f"{prefix}-subtitle", margin, top + 88, content_w, 48,
                  text="A generated interface concept with reusable components and editable vector layers.",
                  role="body", size=16, weight=400),
        component("button", f"{prefix}-primary-action", margin, top + 156, 172, 48,
                  text="Create design", icon="spark", fill=colors["primary"], tone="primary"),
    ])
    card_y = top + (220 if platform == "mobile" else 236)
    cols = 1 if platform == "mobile" else 3
    gap = 16
    card_w = content_w if cols == 1 else int((content_w - gap * (cols - 1)) / cols)
    metric_h = 96 if platform == "mobile" else 120
    metric_step = 108 if platform == "mobile" else 136
    metrics = ["Conversion", "Active users", "Design score"]
    values = ["24.8%", "12.4K", "92"]
    for i, label in enumerate(metrics):
        x = margin + (i % cols) * (card_w + gap)
        y = card_y + (i // cols) * metric_step
        comps.append(component("metric_card", f"{prefix}-metric-{i+1}", x, y, card_w, metric_h,
                               label=label, value=values[i], trend="+8.4%", icon=["chart", "home", "spark"][i]))
    chart_y = card_y + (152 if platform != "mobile" else 336)
    chart_h = 260 if platform != "mobile" else 148
    comps.append(component("chart_card", f"{prefix}-trend", margin, chart_y, content_w, chart_h,
                           title="Interaction trend", values=[42, 56, 51, 68, 74, 88, 81]))
    if platform != "mobile":
        comps.append(component("toast", f"{prefix}-toast", width - 372, 42, 308, 56,
                               title="Design ready", detail="SVG and HTML exports are in sync.", tone="success"))
    if preset == "ecommerce":
        comps.append(component("pricing_card", f"{prefix}-featured-offer", margin, chart_y + 288, 320, 188,
                               title="Starter", price="$29", features=["3 projects", "SVG export", "HTML export"]))
    return {"id": f"frame-{index+1}-{prefix}", "name": name.title(), "w": width, "h": height, "components": comps}


def detail_frame(name: str, index: int, brief: dict, width: int, height: int, colors: dict, preset: str) -> dict:
    platform = brief["platform"]
    prefix = slug(name)
    margin = 24 if platform == "mobile" else 312
    top = 40 if platform == "mobile" else 56
    content_w = width - 48 if platform == "mobile" else width - margin - 56
    comps = nav_components(width, height, platform, colors, prefix)
    comps.extend([
        component("text", f"{prefix}-title", margin, top, content_w, 52,
                  text=f"{name.title()} Details", role="headline", size=32 if platform != "mobile" else 26, weight=800),
        component("search", f"{prefix}-search", margin, top + 76, content_w, 48,
                  placeholder="Search components, states, or copy"),
        component("tabs", f"{prefix}-tabs", margin, top + 140, content_w, 44,
                  labels=["Overview", "Components", "Assets", "Code"], active=1),
    ])
    row_y = top + 204
    if platform == "mobile":
        for i in range(4):
            comps.append(component("list_row", f"{prefix}-row-{i+1}", margin, row_y + i * 88, content_w, 72,
                                   title=f"Design decision {i+1}", detail="Layered structure and clear hierarchy."))
        comps.append(component("modal", f"{prefix}-modal", margin + 12, row_y + 378, content_w - 24, 220,
                               title="Export options", body="Choose the target artifact for the next iteration.",
                               actions=["Cancel", "Export"]))
    else:
        table_w = int(content_w * 0.62)
        comps.append(component("table", f"{prefix}-component-table", margin, row_y, table_w, 320,
                               columns=["Layer", "Type", "Status"],
                               rows=[
                                   ["Primary CTA", "button", "ready"],
                                   ["Metrics", "cards", "ready"],
                                   ["Trend", "chart", "review"],
                                   ["Inspector", "panel", "ready"],
                               ]))
        comps.append(component("form", f"{prefix}-edit-form", margin + table_w + 20, row_y, content_w - table_w - 20, 320,
                               title="Component editor",
                               fields=["Layer name", "Component type", "Visible text"],
                               action="Apply patch"))
        comps.append(component("kanban", f"{prefix}-kanban", margin, row_y + 348, content_w, 228,
                               columns=[
                                   {"title": "Brief", "items": ["Parse audience", "Pick preset"]},
                                   {"title": "Design", "items": ["Build frames", "Add components"]},
                                   {"title": "Export", "items": ["SVG", "HTML", "React"]},
                               ]))
    return {"id": f"frame-{index+1}-{prefix}", "name": name.title(), "w": width, "h": height, "components": comps}


def settings_frame(name: str, index: int, brief: dict, width: int, height: int, colors: dict, preset: str) -> dict:
    platform = brief["platform"]
    prefix = slug(name)
    margin = 24 if platform == "mobile" else 312
    top = 40 if platform == "mobile" else 56
    content_w = width - 48 if platform == "mobile" else width - margin - 56
    comps = nav_components(width, height, platform, colors, prefix)
    comps.extend([
        component("text", f"{prefix}-title", margin, top, content_w, 52,
                  text=f"{name.title()} Settings", role="headline", size=32 if platform != "mobile" else 26, weight=800),
        component("dropdown", f"{prefix}-preset-dropdown", margin, top + 86, min(320, content_w), 54,
                  label="Design preset", value=preset, options=list(PRESETS.keys())),
        component("toggle_row", f"{prefix}-token-mode", margin, top + 164, content_w, 64,
                  title="Use design tokens", enabled=True),
        component("toggle_row", f"{prefix}-auto-layout", margin, top + 244, content_w, 64,
                  title="Prefer auto-layout groups", enabled=True),
        component("toggle_row", f"{prefix}-export-preview", margin, top + 324, content_w, 64,
                  title="Create HTML and React exports", enabled=True),
        component("button", f"{prefix}-save", margin, top + 424, 156, 48, text="Save setup", fill=colors["primary"], tone="primary"),
    ])
    if platform != "mobile":
        comps.append(component("calendar", f"{prefix}-release-calendar", margin + 420, top + 86, 360, 300,
                               title="Design schedule", selected=[5, 12, 18, 24]))
    return {"id": f"frame-{index+1}-{prefix}", "name": name.title(), "w": width, "h": height, "components": comps}


def build_frames(brief: dict, count: int, preset: str) -> list[dict]:
    width, height = frame_size(brief["platform"])
    colors = PRESETS[preset]["colors"]
    requested = list(brief.get("requested_screens") or [])
    defaults = ["overview", "detail", "settings"]
    names = (requested + defaults)[:count]
    frames = []
    for index, name in enumerate(names):
        lname = name.lower()
        if any(word in lname for word in ["setting", "setup", "preference"]):
            frames.append(settings_frame(name, index, brief, width, height, colors, preset))
        elif any(word in lname for word in ["detail", "report", "connect", "account", "analytics"]):
            frames.append(detail_frame(name, index, brief, width, height, colors, preset))
        else:
            frames.append(overview_frame(name, index, brief, width, height, colors, preset))
    return frames


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--brief-file", required=True)
    parser.add_argument("--screens", type=int)
    parser.add_argument("--preset", choices=sorted(PRESETS))
    parser.add_argument("--output")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    brief_path = Path(args.brief_file)
    if not brief_path.is_absolute():
        brief_path = project / brief_path
    brief = load_json(brief_path)
    count = args.screens or int(brief.get("screen_count", 3))
    count = max(1, min(8, count))
    preset = pick_preset(brief, args.preset)
    tokens = PRESETS[preset]
    spec = {
        "name": f"{brief['product'].title()} UI Concept",
        "target_tool": "Lunacy",
        "source": "llm-editable-json",
        "design_preset": preset,
        "assets": asset_manifest(preset),
        "brief": brief,
        "tokens": {
            "colors": tokens["colors"],
            "font": {"family": "Inter, Arial, sans-serif", "base": 16},
            "spacing": {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 40},
            "radius": tokens["radius"],
            "density": tokens["density"],
        },
        "component_catalog": [
            "button", "nav_item", "bottom_nav", "metric_card", "chart_card", "search",
            "tabs", "dropdown", "table", "form", "modal", "toast", "pricing_card",
            "calendar", "kanban", "image_placeholder",
        ],
        "frames": build_frames(brief, count, preset),
    }

    output = Path(args.output) if args.output else project / ".opencode/work/lunacy_screens.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not args.force:
        raise SystemExit(f"{output} already exists. Use --force to overwrite.")
    output.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
