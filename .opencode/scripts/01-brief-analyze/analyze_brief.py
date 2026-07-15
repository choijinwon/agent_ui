#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def read_text(value: str | None, file_path: str | None) -> str:
    if value:
        return value.strip()
    if file_path:
        return Path(file_path).read_text(encoding="utf-8").strip()
    raise SystemExit("Provide --brief or --brief-file.")


def detect_platform(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["mobile", "iphone", "android", "app", "phone"]):
        return "mobile"
    if any(word in lowered for word in ["tablet", "ipad"]):
        return "tablet"
    if any(word in lowered for word in ["desktop", "web", "dashboard", "admin", "saas"]):
        return "desktop"
    return "desktop"


def detect_style(text: str) -> list[str]:
    lowered = text.lower()
    styles = []
    checks = {
        "professional": ["professional", "executive", "b2b", "enterprise", "trust"],
        "minimal": ["minimal", "simple", "clean", "plain"],
        "editorial": ["editorial", "magazine", "content"],
        "playful": ["playful", "friendly", "fun", "creator"],
        "dark": ["dark", "black", "night"],
        "light": ["light", "white", "bright"],
        "data-dense": ["dashboard", "analytics", "metrics", "data", "finance"],
    }
    for name, words in checks.items():
        if any(word in lowered for word in words):
            styles.append(name)
    return styles or ["clean", "focused", "professional"]


def detect_audience(text: str) -> str:
    lowered = text.lower()
    patterns = [
        (["executive", "leadership", "ceo", "cfo"], "executives"),
        (["developer", "engineer"], "technical users"),
        (["designer", "creative"], "designers"),
        (["student", "education"], "students"),
        (["office", "worker", "employee"], "office workers"),
        (["consumer", "customer", "user"], "general users"),
    ]
    for words, audience in patterns:
        if any(word in lowered for word in words):
            return audience
    return "general users"


def detect_product(text: str) -> str:
    lowered = text.lower()
    products = [
        ("finance dashboard", ["finance", "spending", "budget", "bank"]),
        ("AI assistant", ["ai", "llm", "assistant", "agent"]),
        ("admin dashboard", ["admin", "dashboard", "operations"]),
        ("commerce app", ["shop", "commerce", "product", "cart"]),
        ("learning product", ["course", "learn", "education", "student"]),
        ("project workspace", ["project", "task", "workspace", "team"]),
    ]
    for name, words in products:
        if any(word in lowered for word in words):
            return name
    first_sentence = re.split(r"[.!?\n]", text.strip())[0].strip()
    return first_sentence[:80] if first_sentence else "digital product"


def detect_screens(text: str) -> list[str]:
    lowered = text.lower()
    names = []
    screen_map = {
        "welcome": ["welcome", "onboarding", "intro"],
        "overview": ["overview", "home", "dashboard"],
        "detail": ["detail", "report", "profile"],
        "settings": ["settings", "preferences"],
        "checkout": ["checkout", "payment", "cart"],
        "account connection": ["connect", "account", "bank"],
        "analytics": ["analytics", "metrics", "chart"],
    }
    for name, words in screen_map.items():
        if any(word in lowered for word in words):
            names.append(name)
    match = re.search(r"(?:screens?|pages?|views?)\s*[:=]?\s*([A-Za-z0-9,\- /]+)", text, re.I)
    if match:
        for part in re.split(r"[,/]", match.group(1)):
            cleaned = part.strip(" .")
            if cleaned and len(cleaned) < 32:
                names.append(cleaned.lower())
    deduped = []
    for name in names:
        if name not in deduped:
            deduped.append(name)
    return deduped or ["overview", "detail", "settings"]


def detect_must_haves(text: str) -> list[str]:
    lowered = text.lower()
    items = []
    checks = {
        "primary CTA": ["cta", "button", "signup", "start", "continue"],
        "navigation": ["nav", "menu", "tabs", "sidebar"],
        "summary metrics": ["metric", "summary", "kpi", "dashboard"],
        "charts": ["chart", "graph", "trend"],
        "cards": ["card", "tile"],
        "search": ["search", "filter"],
        "form": ["form", "input", "connect"],
    }
    for item, words in checks.items():
        if any(word in lowered for word in words):
            items.append(item)
    return items or ["primary CTA", "navigation", "clear content hierarchy"]


def parse_screen_count(text: str, fallback: int) -> int:
    match = re.search(r"(\d+)\s*(?:screens?|pages?|views?|장)", text, re.I)
    if not match:
        return fallback
    return max(1, min(8, int(match.group(1))))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--brief")
    parser.add_argument("--brief-file")
    parser.add_argument("--output")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    text = read_text(args.brief, args.brief_file)
    screens = detect_screens(text)
    screen_count = parse_screen_count(text, len(screens))

    output = Path(args.output) if args.output else project / ".opencode/work/lunacy_brief.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not args.force:
        raise SystemExit(f"{output} already exists. Use --force to overwrite.")

    data = {
        "source_brief": text,
        "product": detect_product(text),
        "audience": detect_audience(text),
        "platform": detect_platform(text),
        "style": detect_style(text),
        "screen_count": screen_count,
        "requested_screens": screens[:screen_count],
        "must_haves": detect_must_haves(text),
        "constraints": {
            "editable_source": "json",
            "primary_design_output": "svg",
            "target_tool": "Lunacy",
        },
    }

    output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
