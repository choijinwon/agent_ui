#!/usr/bin/env python3
import argparse
import json
import re
from copy import deepcopy
from pathlib import Path


PRESET_COLORS = {
    "dark": {
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
    "light": {
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
    "fintech": {
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
    "admin": {
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
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_value(value: str) -> object:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def path_parts(path: str) -> list[str | int]:
    parts: list[str | int] = []
    for item in path.split("."):
        if item.isdigit():
            parts.append(int(item))
        else:
            parts.append(item)
    return parts


def set_path(data: dict, path: str, value: object) -> None:
    parts = path_parts(path)
    cursor: object = data
    for part in parts[:-1]:
        cursor = cursor[part]  # type: ignore[index]
    cursor[parts[-1]] = value  # type: ignore[index]


def first_frame(spec: dict) -> dict:
    if not spec.get("frames"):
        raise SystemExit("Spec has no frames.")
    return spec["frames"][0]


def component(kind: str, cid: str, x: int, y: int, w: int, h: int, **extra) -> dict:
    data = {"id": cid, "type": kind, "x": x, "y": y, "w": w, "h": h}
    data.update(extra)
    return data


def add_component(spec: dict, kind: str) -> str:
    frame = first_frame(spec)
    colors = spec.get("tokens", {}).get("colors", {})
    base_x = 312 if frame["w"] > 700 else 24
    base_y = min(frame["h"] - 240, 620)
    prefix = f"patch-{kind}-{len(frame.get('components', [])) + 1}"
    modal_w = min(420, frame["w"] - 48)
    modal_x = max(24, int((frame["w"] - modal_w) / 2))
    toast_w = min(308, frame["w"] - 48)
    toast_x = max(24, frame["w"] - toast_w - 24)
    samples = {
        "modal": component("modal", prefix, modal_x, base_y - 120, modal_w, 220,
                           title="Confirm export", body="Review the generated design before pushing artifacts.",
                           actions=["Cancel", "Export"]),
        "table": component("table", prefix, base_x, base_y, min(620, frame["w"] - base_x - 40), 260,
                           columns=["Name", "Type", "State"],
                           rows=[["Hero", "section", "ready"], ["CTA", "button", "ready"], ["Chart", "card", "review"]]),
        "tabs": component("tabs", prefix, base_x, base_y, min(520, frame["w"] - base_x - 40), 44,
                          labels=["Overview", "Design", "Code"], active=0),
        "pricing": component("pricing_card", prefix, base_x, base_y, 320, 188,
                             title="Pro", price="$49", features=["React export", "HTML export", "Patch loop"]),
        "calendar": component("calendar", prefix, base_x, base_y - 40, 360, 300,
                              title="Release calendar", selected=[3, 10, 17, 25]),
        "kanban": component("kanban", prefix, base_x, base_y - 30, min(760, frame["w"] - base_x - 40), 228,
                            columns=[
                                {"title": "Todo", "items": ["Add assets", "Pick preset"]},
                                {"title": "Doing", "items": ["Render HTML"]},
                                {"title": "Done", "items": ["Review"]},
                            ]),
        "form": component("form", prefix, base_x, base_y - 30, 360, 300,
                          title="Edit component", fields=["Name", "Type", "Text"], action="Apply patch"),
        "toast": component("toast", prefix, toast_x, 42, toast_w, 56,
                           title="Patched", detail="Design JSON was updated.", tone="success"),
        "image": component("image_placeholder", prefix, base_x, base_y - 20, 360, 220,
                           label="Product image placeholder"),
    }
    if kind not in samples:
        raise SystemExit(f"Unknown component kind: {kind}")
    if samples[kind]["type"] == "button":
        samples[kind]["fill"] = colors.get("primary", "#2563EB")
    frame.setdefault("components", []).append(samples[kind])
    catalog = spec.setdefault("component_catalog", [])
    if samples[kind]["type"] not in catalog:
        catalog.append(samples[kind]["type"])
    return f"added {samples[kind]['type']} to {frame.get('name', 'first frame')}"


def apply_instruction(spec: dict, instruction: str) -> list[str]:
    lowered = instruction.lower()
    changes = []
    for preset in ["dark", "light", "fintech", "admin"]:
        if preset in lowered or (preset == "dark" and "dark mode" in lowered):
            spec["design_preset"] = preset
            spec.setdefault("tokens", {})["colors"] = deepcopy(PRESET_COLORS[preset])
            changes.append(f"applied {preset} colors")
            break
    if "primary" in lowered and "#" in lowered:
        match = re.search(r"#[0-9a-fA-F]{6}", instruction)
        if match:
            spec.setdefault("tokens", {}).setdefault("colors", {})["primary"] = match.group(0)
            changes.append(f"set primary color to {match.group(0)}")
    add_map = {
        "modal": ["modal", "dialog"],
        "table": ["table", "grid"],
        "tabs": ["tab", "tabs"],
        "pricing": ["pricing", "price", "plan"],
        "calendar": ["calendar", "schedule"],
        "kanban": ["kanban", "board"],
        "form": ["form", "input"],
        "toast": ["toast", "notification"],
        "image": ["image", "asset", "photo"],
    }
    for kind, words in add_map.items():
        if any(word in lowered for word in words) and any(word in lowered for word in ["add", "insert", "create", "추가"]):
            changes.append(add_component(spec, kind))
            break
    title_match = re.search(r'title\s*=\s*"([^"]+)"', instruction, re.I)
    if title_match:
        for component_item in first_frame(spec).get("components", []):
            if component_item.get("role") == "headline":
                component_item["text"] = title_match.group(1)
                changes.append("updated first headline title")
                break
    return changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--instruction")
    parser.add_argument("--set", action="append", default=[], dest="sets",
                        help="Set a JSON path, for example frames.0.components.1.text=Hello")
    parser.add_argument("--output")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    spec_path = Path(args.spec)
    if not spec_path.is_absolute():
        spec_path = project / spec_path
    output = Path(args.output) if args.output else spec_path
    if not output.is_absolute():
        output = project / output
    if output.exists() and output != spec_path and not args.force:
        raise SystemExit(f"{output} already exists. Use --force to overwrite.")

    spec = load_json(spec_path)
    changes = []
    if args.instruction:
        changes.extend(apply_instruction(spec, args.instruction))
    for assignment in args.sets:
        if "=" not in assignment:
            raise SystemExit(f"--set must be path=value: {assignment}")
        path, raw_value = assignment.split("=", 1)
        set_path(spec, path, parse_value(raw_value))
        changes.append(f"set {path}")
    if not changes:
        raise SystemExit("No changes requested. Provide --instruction or --set.")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    print(json.dumps({"changes": changes}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
