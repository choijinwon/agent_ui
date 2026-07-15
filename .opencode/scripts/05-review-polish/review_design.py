#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path
from xml.etree import ElementTree


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    value = value.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return tuple(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))


def channel(value: float) -> float:
    return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    r, g, b = hex_to_rgb(hex_color)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    light, dark = max(la, lb), min(la, lb)
    return (light + 0.05) / (dark + 0.05)


def component_text(component: dict) -> str:
    return component.get("text") or component.get("title") or component.get("label") or component.get("placeholder") or ""


def approx_text_width(text: str, size: int) -> float:
    return len(text) * size * 0.54


def review_spec(spec: dict) -> list[dict]:
    issues = []
    colors = spec.get("tokens", {}).get("colors", {})
    frames = spec.get("frames", [])
    if not frames:
        issues.append({"severity": "error", "message": "No frames in screen spec."})
    ids = set()
    for frame in frames:
        if not frame.get("name"):
            issues.append({"severity": "error", "message": f"{frame.get('id', 'frame')} has no name."})
        components = frame.get("components", [])
        if not components:
            issues.append({"severity": "error", "message": f"{frame.get('name', 'Frame')} has no components."})
        for component in components:
            cid = component.get("id")
            if not cid:
                issues.append({"severity": "error", "message": f"{frame.get('name', 'Frame')} has a component without an ID."})
                continue
            if cid in ids:
                issues.append({"severity": "error", "message": f"Duplicate component ID: {cid}"})
            ids.add(cid)
            text = component_text(component)
            if text and component.get("w"):
                size = int(component.get("size", 15))
                if approx_text_width(text, size) > component["w"] * 2.8:
                    issues.append({"severity": "warning", "message": f"Long text may overflow in {cid}."})
            if component["type"] == "button" and (component.get("h", 0) < 44 or component.get("w", 0) < 44):
                issues.append({"severity": "warning", "message": f"Button {cid} is smaller than a comfortable target."})
            x, y = component.get("x", 0), component.get("y", 0)
            w, h = component.get("w", 0), component.get("h", 0)
            if x < 0 or y < 0 or x + w > frame.get("w", 0) or y + h > frame.get("h", 0):
                issues.append({"severity": "warning", "message": f"Component {cid} extends outside {frame.get('name', 'frame')}."})
    if colors:
        try:
            body_ratio = contrast(colors["text"], colors["canvas"])
            muted_ratio = contrast(colors["muted"], colors["canvas"])
            if body_ratio < 4.5:
                issues.append({"severity": "warning", "message": f"Text contrast on canvas is {body_ratio:.2f}:1."})
            if muted_ratio < 3:
                issues.append({"severity": "warning", "message": f"Muted text contrast on canvas is {muted_ratio:.2f}:1."})
        except (KeyError, ValueError):
            issues.append({"severity": "warning", "message": "Could not evaluate color contrast."})
    return issues


def review_svg(svg_path: Path) -> list[dict]:
    issues = []
    try:
        tree = ElementTree.parse(svg_path)
    except ElementTree.ParseError as exc:
        return [{"severity": "error", "message": f"SVG is not valid XML: {exc}"}]
    root = tree.getroot()
    width = root.attrib.get("width")
    height = root.attrib.get("height")
    if not width or not height:
        issues.append({"severity": "warning", "message": "SVG is missing width or height."})
    groups = root.findall(".//{http://www.w3.org/2000/svg}g")
    if len(groups) < 3:
        issues.append({"severity": "warning", "message": "SVG has very few groups; layer tree may be too flat."})
    return issues


def review_html(html_path: Path | None, expected_frames: int) -> list[dict]:
    issues = []
    if not html_path:
        return issues
    if not html_path.exists():
        return [{"severity": "error", "message": f"Missing HTML: {html_path}"}]
    content = html_path.read_text(encoding="utf-8")
    if "<!doctype html>" not in content.lower():
        issues.append({"severity": "warning", "message": "HTML output does not declare a doctype."})
    frame_count = content.count('class="screen-frame"')
    if frame_count != expected_frames:
        issues.append({"severity": "warning", "message": f"HTML has {frame_count} screen frames; expected {expected_frames}."})
    if "data-layer-id=" not in content:
        issues.append({"severity": "warning", "message": "HTML is missing data-layer-id attributes."})
    if "<style>" not in content or "</style>" not in content:
        issues.append({"severity": "warning", "message": "HTML is missing embedded CSS."})
    return issues


def review_react(react_path: Path | None) -> list[dict]:
    issues = []
    if not react_path:
        return issues
    if not react_path.exists():
        return [{"severity": "error", "message": f"Missing React export: {react_path}"}]
    content = react_path.read_text(encoding="utf-8")
    if "export default function" not in content:
        issues.append({"severity": "warning", "message": "React export does not include a default component export."})
    if "className=" not in content:
        issues.append({"severity": "warning", "message": "React export does not include Tailwind/className styling."})
    if "data-layer-id=" not in content:
        issues.append({"severity": "warning", "message": "React export is missing data-layer-id attributes."})
    if "React.CSSProperties" not in content:
        issues.append({"severity": "warning", "message": "React export is missing token style typing."})
    return issues


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--svg", required=True)
    parser.add_argument("--html")
    parser.add_argument("--react")
    parser.add_argument("--output")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    spec_path = Path(args.spec)
    svg_path = Path(args.svg)
    html_path = Path(args.html) if args.html else None
    react_path = Path(args.react) if args.react else None
    if not spec_path.is_absolute():
        spec_path = project / spec_path
    if not svg_path.is_absolute():
        svg_path = project / svg_path
    if html_path and not html_path.is_absolute():
        html_path = project / html_path
    if react_path and not react_path.is_absolute():
        react_path = project / react_path
    output = Path(args.output) if args.output else project / ".opencode/work/lunacy_review.json"

    if not spec_path.exists():
        raise SystemExit(f"Missing spec: {spec_path}")
    if not svg_path.exists():
        raise SystemExit(f"Missing SVG: {svg_path}")

    spec = load_json(spec_path)
    expected_frames = len(spec.get("frames", []))
    issues = review_spec(spec) + review_svg(svg_path) + review_html(html_path, expected_frames) + review_react(react_path)
    error_count = sum(1 for issue in issues if issue["severity"] == "error")
    warning_count = sum(1 for issue in issues if issue["severity"] == "warning")
    report = {
        "ok": error_count == 0,
        "error_count": error_count,
        "warning_count": warning_count,
        "issues": issues,
        "score": max(0, int(100 - error_count * 30 - warning_count * 8 - math.log2(max(1, warning_count + 1)))),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if error_count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
