#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


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


def palette(styles: list[str]) -> dict:
    if "dark" in styles:
        return {
            "canvas": "#0B1020",
            "surface": "#151B2E",
            "surface_alt": "#202842",
            "text": "#F5F7FB",
            "muted": "#A8B0C4",
            "primary": "#56CCF2",
            "secondary": "#F2C94C",
            "success": "#6FCF97",
            "danger": "#EB5757",
            "line": "#313A56",
        }
    return {
        "canvas": "#F5F7FA",
        "surface": "#FFFFFF",
        "surface_alt": "#EEF2F7",
        "text": "#172033",
        "muted": "#5B667A",
        "primary": "#2563EB",
        "secondary": "#14B8A6",
        "success": "#16A34A",
        "danger": "#DC2626",
        "line": "#D7DEE8",
    }


def component(kind: str, cid: str, x: int, y: int, w: int, h: int, **extra) -> dict:
    data = {"id": cid, "type": kind, "x": x, "y": y, "w": w, "h": h}
    data.update(extra)
    return data


def nav_components(width: int, height: int, platform: str, colors: dict, prefix: str) -> list[dict]:
    if platform == "mobile":
        return [
            component("bottom_nav", f"{prefix}-bottom-nav", 16, height - 84, width - 32, 64,
                      labels=["Home", "Insights", "Cards", "Settings"], fill=colors["surface"]),
        ]
    return [
        component("sidebar", f"{prefix}-sidebar", 24, 24, 248, height - 48, fill=colors["surface"]),
        component("text", f"{prefix}-brand-title", 48, 52, 180, 28, text="Lunacy Agent", role="brand", size=20, weight=700),
        component("nav_item", f"{prefix}-nav-overview", 48, 120, 176, 40, text="Overview", active=True),
        component("nav_item", f"{prefix}-nav-designs", 48, 168, 176, 40, text="Designs", active=False),
        component("nav_item", f"{prefix}-nav-settings", 48, 216, 176, 40, text="Settings", active=False),
    ]


def overview_frame(name: str, index: int, brief: dict, width: int, height: int, colors: dict) -> dict:
    platform = brief["platform"]
    prefix = slug(name)
    margin = 24 if platform == "mobile" else 312
    top = 40 if platform == "mobile" else 56
    content_w = width - 48 if platform == "mobile" else width - margin - 56
    title = f"{brief['product'].title()} {name.title()}"
    comps = nav_components(width, height, platform, colors, prefix)
    comps.extend([
        component("text", f"{slug(name)}-eyebrow", margin, top, content_w, 20,
                  text=brief["audience"].upper(), role="eyebrow", size=12, weight=700),
        component("text", f"{slug(name)}-title", margin, top + 28, content_w, 54,
                  text=title, role="headline", size=34 if platform != "mobile" else 28, weight=800),
        component("text", f"{slug(name)}-subtitle", margin, top + 88, content_w, 48,
                  text="A generated interface concept with reusable components and editable vector layers.",
                  role="body", size=16, weight=400),
        component("button", f"{slug(name)}-primary-action", margin, top + 156, 172, 48,
                  text="Create design", fill=colors["primary"], tone="primary"),
    ])
    card_y = top + 236
    cols = 1 if platform == "mobile" else 3
    gap = 16
    card_w = content_w if cols == 1 else int((content_w - gap * (cols - 1)) / cols)
    metrics = ["Conversion", "Active users", "Design score"]
    values = ["24.8%", "12.4K", "92"]
    for i, label in enumerate(metrics):
        x = margin + (i % cols) * (card_w + gap)
        y = card_y + (i // cols) * 136
        comps.append(component("metric_card", f"{slug(name)}-metric-{i+1}", x, y, card_w, 120,
                               label=label, value=values[i], trend="+8.4%"))
    chart_y = card_y + (152 if platform != "mobile" else 424)
    comps.append(component("chart_card", f"{slug(name)}-trend", margin, chart_y, content_w, 260,
                           title="Interaction trend", values=[42, 56, 51, 68, 74, 88, 81]))
    return {"id": f"frame-{index+1}-{slug(name)}", "name": name.title(), "w": width, "h": height, "components": comps}


def detail_frame(name: str, index: int, brief: dict, width: int, height: int, colors: dict) -> dict:
    platform = brief["platform"]
    prefix = slug(name)
    margin = 24 if platform == "mobile" else 312
    top = 40 if platform == "mobile" else 56
    content_w = width - 48 if platform == "mobile" else width - margin - 56
    comps = nav_components(width, height, platform, colors, prefix)
    comps.extend([
        component("text", f"{slug(name)}-title", margin, top, content_w, 52,
                  text=f"{name.title()} Details", role="headline", size=32 if platform != "mobile" else 26, weight=800),
        component("search", f"{slug(name)}-search", margin, top + 76, content_w, 48,
                  placeholder="Search components, states, or copy"),
    ])
    row_y = top + 152
    for i in range(4):
        comps.append(component("list_row", f"{slug(name)}-row-{i+1}", margin, row_y + i * 88, content_w, 72,
                               title=f"Design decision {i+1}", detail="Layered structure, tokenized style, and clear hierarchy."))
    comps.append(component("inspector", f"{slug(name)}-inspector", margin, row_y + 384, content_w, 220,
                           title="LLM edit target", body="Update JSON values, regenerate SVG, then review."))
    return {"id": f"frame-{index+1}-{slug(name)}", "name": name.title(), "w": width, "h": height, "components": comps}


def settings_frame(name: str, index: int, brief: dict, width: int, height: int, colors: dict) -> dict:
    platform = brief["platform"]
    prefix = slug(name)
    margin = 24 if platform == "mobile" else 312
    top = 40 if platform == "mobile" else 56
    content_w = width - 48 if platform == "mobile" else width - margin - 56
    comps = nav_components(width, height, platform, colors, prefix)
    comps.extend([
        component("text", f"{slug(name)}-title", margin, top, content_w, 52,
                  text=f"{name.title()} Settings", role="headline", size=32 if platform != "mobile" else 26, weight=800),
        component("toggle_row", f"{slug(name)}-token-mode", margin, top + 92, content_w, 64,
                  title="Use design tokens", enabled=True),
        component("toggle_row", f"{slug(name)}-auto-layout", margin, top + 172, content_w, 64,
                  title="Prefer auto-layout groups", enabled=True),
        component("toggle_row", f"{slug(name)}-export-preview", margin, top + 252, content_w, 64,
                  title="Create HTML preview", enabled=True),
        component("button", f"{slug(name)}-save", margin, top + 352, 156, 48, text="Save setup", fill=colors["primary"], tone="primary"),
    ])
    return {"id": f"frame-{index+1}-{slug(name)}", "name": name.title(), "w": width, "h": height, "components": comps}


def build_frames(brief: dict, count: int) -> list[dict]:
    width, height = frame_size(brief["platform"])
    colors = palette(brief.get("style", []))
    requested = list(brief.get("requested_screens") or [])
    defaults = ["overview", "detail", "settings"]
    names = (requested + defaults)[:count]
    frames = []
    for index, name in enumerate(names):
        lname = name.lower()
        if any(word in lname for word in ["setting", "setup", "preference"]):
            frames.append(settings_frame(name, index, brief, width, height, colors))
        elif any(word in lname for word in ["detail", "report", "connect", "account", "analytics"]):
            frames.append(detail_frame(name, index, brief, width, height, colors))
        else:
            frames.append(overview_frame(name, index, brief, width, height, colors))
    return frames


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--brief-file", required=True)
    parser.add_argument("--screens", type=int)
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
    colors = palette(brief.get("style", []))
    spec = {
        "name": f"{brief['product'].title()} UI Concept",
        "target_tool": "Lunacy",
        "source": "llm-editable-json",
        "brief": brief,
        "tokens": {
            "colors": colors,
            "font": {"family": "Inter, Arial, sans-serif", "base": 16},
            "spacing": {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 40},
            "radius": {"sm": 6, "md": 8, "lg": 12},
        },
        "frames": build_frames(brief, count),
    }

    output = Path(args.output) if args.output else project / ".opencode/work/lunacy_screens.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not args.force:
        raise SystemExit(f"{output} already exists. Use --force to overwrite.")
    output.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
