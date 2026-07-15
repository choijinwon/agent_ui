#!/usr/bin/env python3
import argparse
import html
import json
import re
from pathlib import Path


def slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_") or "entity"


def pascal(value: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[^A-Za-z0-9]+", value) if part) or "Entity"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_context(project: Path, brief_file: str | None, spec_file: str | None, brief_text: str | None) -> dict:
    if spec_file:
        path = Path(spec_file)
        if not path.is_absolute():
            path = project / path
        spec = load_json(path)
        brief = spec.get("brief", {})
        return {"spec": spec, "brief": brief, "text": brief.get("source_brief", "")}
    if brief_file:
        path = Path(brief_file)
        if not path.is_absolute():
            path = project / path
        brief = load_json(path)
        return {"brief": brief, "text": brief.get("source_brief", "")}
    if brief_text:
        return {"brief": {"source_brief": brief_text, "product": "digital product"}, "text": brief_text}
    raise SystemExit("Provide --spec, --brief-file, or --brief.")


def detect_domain(text: str, product: str, requested: str | None) -> str:
    if requested:
        return requested
    haystack = f"{text} {product}".lower()
    if any(word in haystack for word in ["finance", "bank", "budget", "spending", "payment", "card"]):
        return "finance"
    if any(word in haystack for word in ["shop", "commerce", "cart", "order", "product", "inventory"]):
        return "commerce"
    if any(word in haystack for word in ["project", "task", "workspace", "team", "kanban"]):
        return "workspace"
    if any(word in haystack for word in ["course", "lesson", "student", "learning", "education"]):
        return "learning"
    return "saas"


def field(name: str, kind: str, required: bool = True, pk: bool = False, fk: str | None = None) -> dict:
    data = {"name": name, "type": kind, "required": required, "primary_key": pk}
    if fk:
        data["foreign_key"] = fk
    return data


def entity(name: str, fields: list[dict]) -> dict:
    return {"name": name, "table": slug(name), "fields": fields}


def base_entities(domain: str) -> tuple[list[dict], list[dict]]:
    common_user = entity("User", [
        field("id", "uuid", pk=True),
        field("email", "varchar"),
        field("name", "varchar"),
        field("created_at", "timestamp"),
    ])
    if domain == "finance":
        entities = [
            common_user,
            entity("Account", [
                field("id", "uuid", pk=True),
                field("user_id", "uuid", fk="User.id"),
                field("provider", "varchar"),
                field("account_type", "varchar"),
                field("balance", "decimal"),
                field("connected_at", "timestamp"),
            ]),
            entity("Transaction", [
                field("id", "uuid", pk=True),
                field("account_id", "uuid", fk="Account.id"),
                field("category_id", "uuid", fk="Category.id"),
                field("amount", "decimal"),
                field("description", "varchar"),
                field("posted_at", "timestamp"),
            ]),
            entity("Category", [
                field("id", "uuid", pk=True),
                field("name", "varchar"),
                field("kind", "varchar"),
            ]),
            entity("Budget", [
                field("id", "uuid", pk=True),
                field("user_id", "uuid", fk="User.id"),
                field("category_id", "uuid", fk="Category.id"),
                field("limit_amount", "decimal"),
                field("period", "varchar"),
            ]),
        ]
        relationships = [
            rel("User", "Account", "one-to-many", "owns"),
            rel("Account", "Transaction", "one-to-many", "records"),
            rel("Category", "Transaction", "one-to-many", "classifies"),
            rel("User", "Budget", "one-to-many", "sets"),
            rel("Category", "Budget", "one-to-many", "limits"),
        ]
        return entities, relationships
    if domain == "commerce":
        entities = [
            common_user,
            entity("Product", [
                field("id", "uuid", pk=True),
                field("name", "varchar"),
                field("price", "decimal"),
                field("status", "varchar"),
            ]),
            entity("Order", [
                field("id", "uuid", pk=True),
                field("user_id", "uuid", fk="User.id"),
                field("status", "varchar"),
                field("total_amount", "decimal"),
                field("ordered_at", "timestamp"),
            ]),
            entity("OrderItem", [
                field("id", "uuid", pk=True),
                field("order_id", "uuid", fk="Order.id"),
                field("product_id", "uuid", fk="Product.id"),
                field("quantity", "integer"),
                field("unit_price", "decimal"),
            ]),
            entity("Payment", [
                field("id", "uuid", pk=True),
                field("order_id", "uuid", fk="Order.id"),
                field("provider", "varchar"),
                field("status", "varchar"),
                field("paid_at", "timestamp", required=False),
            ]),
        ]
        relationships = [
            rel("User", "Order", "one-to-many", "places"),
            rel("Order", "OrderItem", "one-to-many", "contains"),
            rel("Product", "OrderItem", "one-to-many", "appears_in"),
            rel("Order", "Payment", "one-to-one", "paid_by"),
        ]
        return entities, relationships
    if domain == "workspace":
        entities = [
            common_user,
            entity("Workspace", [
                field("id", "uuid", pk=True),
                field("name", "varchar"),
                field("created_at", "timestamp"),
            ]),
            entity("Project", [
                field("id", "uuid", pk=True),
                field("workspace_id", "uuid", fk="Workspace.id"),
                field("name", "varchar"),
                field("status", "varchar"),
            ]),
            entity("Task", [
                field("id", "uuid", pk=True),
                field("project_id", "uuid", fk="Project.id"),
                field("assignee_id", "uuid", fk="User.id"),
                field("title", "varchar"),
                field("status", "varchar"),
                field("due_at", "timestamp", required=False),
            ]),
        ]
        relationships = [
            rel("Workspace", "Project", "one-to-many", "contains"),
            rel("Project", "Task", "one-to-many", "tracks"),
            rel("User", "Task", "one-to-many", "assigned"),
        ]
        return entities, relationships
    if domain == "learning":
        entities = [
            common_user,
            entity("Course", [
                field("id", "uuid", pk=True),
                field("title", "varchar"),
                field("level", "varchar"),
            ]),
            entity("Lesson", [
                field("id", "uuid", pk=True),
                field("course_id", "uuid", fk="Course.id"),
                field("title", "varchar"),
                field("position", "integer"),
            ]),
            entity("Enrollment", [
                field("id", "uuid", pk=True),
                field("user_id", "uuid", fk="User.id"),
                field("course_id", "uuid", fk="Course.id"),
                field("status", "varchar"),
                field("enrolled_at", "timestamp"),
            ]),
        ]
        relationships = [
            rel("Course", "Lesson", "one-to-many", "contains"),
            rel("User", "Enrollment", "one-to-many", "has"),
            rel("Course", "Enrollment", "one-to-many", "includes"),
        ]
        return entities, relationships
    entities = [
        common_user,
        entity("Organization", [
            field("id", "uuid", pk=True),
            field("name", "varchar"),
            field("plan", "varchar"),
        ]),
        entity("Membership", [
            field("id", "uuid", pk=True),
            field("user_id", "uuid", fk="User.id"),
            field("organization_id", "uuid", fk="Organization.id"),
            field("role", "varchar"),
        ]),
        entity("Activity", [
            field("id", "uuid", pk=True),
            field("organization_id", "uuid", fk="Organization.id"),
            field("actor_id", "uuid", fk="User.id"),
            field("event_type", "varchar"),
            field("created_at", "timestamp"),
        ]),
    ]
    relationships = [
        rel("User", "Membership", "one-to-many", "has"),
        rel("Organization", "Membership", "one-to-many", "includes"),
        rel("Organization", "Activity", "one-to-many", "logs"),
        rel("User", "Activity", "one-to-many", "performs"),
    ]
    return entities, relationships


def rel(left: str, right: str, cardinality: str, label: str) -> dict:
    return {"left": left, "right": right, "cardinality": cardinality, "label": label}


def add_screen_entities(entities: list[dict], relationships: list[dict], spec: dict | None) -> None:
    if not spec:
        return
    names = [frame.get("name", "") for frame in spec.get("frames", [])]
    if any("setting" in name.lower() for name in names):
        entities.append(entity("Preference", [
            field("id", "uuid", pk=True),
            field("user_id", "uuid", fk="User.id"),
            field("key", "varchar"),
            field("value", "json"),
        ]))
        relationships.append(rel("User", "Preference", "one-to-many", "configures"))
    if any("notification" in name.lower() or "alert" in name.lower() for name in names):
        entities.append(entity("Notification", [
            field("id", "uuid", pk=True),
            field("user_id", "uuid", fk="User.id"),
            field("title", "varchar"),
            field("read_at", "timestamp", required=False),
        ]))
        relationships.append(rel("User", "Notification", "one-to-many", "receives"))


def dedupe_entities(entities: list[dict]) -> list[dict]:
    seen = set()
    output = []
    for item in entities:
        if item["name"] in seen:
            continue
        seen.add(item["name"])
        output.append(item)
    return output


def mermaid_type(sql_type: str) -> str:
    return {
        "uuid": "string",
        "varchar": "string",
        "decimal": "decimal",
        "integer": "int",
        "timestamp": "datetime",
        "json": "json",
    }.get(sql_type, "string")


def relationship_symbol(cardinality: str) -> str:
    return {
        "one-to-one": "||--||",
        "one-to-many": "||--o{",
        "many-to-one": "}o--||",
        "many-to-many": "}o--o{",
    }.get(cardinality, "||--o{")


def render_mermaid(erd: dict) -> str:
    lines = ["erDiagram"]
    for item in erd["entities"]:
        lines.append(f"  {pascal(item['name'])} {{")
        for item_field in item["fields"]:
            markers = []
            if item_field.get("primary_key"):
                markers.append("PK")
            if item_field.get("foreign_key"):
                markers.append("FK")
            suffix = f" \"{', '.join(markers)}\"" if markers else ""
            lines.append(f"    {mermaid_type(item_field['type'])} {item_field['name']}{suffix}")
        lines.append("  }")
    for item in erd["relationships"]:
        lines.append(
            f"  {pascal(item['left'])} {relationship_symbol(item['cardinality'])} "
            f"{pascal(item['right'])} : {item['label']}"
        )
    return "\n".join(lines) + "\n"


def sql_type(kind: str) -> str:
    return {
        "uuid": "UUID",
        "varchar": "VARCHAR(255)",
        "decimal": "DECIMAL(12,2)",
        "integer": "INTEGER",
        "timestamp": "TIMESTAMP",
        "json": "JSONB",
    }.get(kind, "VARCHAR(255)")


def render_sql(erd: dict) -> str:
    statements = []
    for item in erd["entities"]:
        columns = []
        constraints = []
        for item_field in item["fields"]:
            nullable = " NOT NULL" if item_field.get("required", True) or item_field.get("primary_key") else ""
            columns.append(f"  {item_field['name']} {sql_type(item_field['type'])}{nullable}")
            if item_field.get("primary_key"):
                constraints.append(f"  PRIMARY KEY ({item_field['name']})")
            if item_field.get("foreign_key"):
                table_name, field_name = item_field["foreign_key"].split(".")
                constraints.append(
                    f"  FOREIGN KEY ({item_field['name']}) REFERENCES {slug(table_name)}({field_name})"
                )
        body = ",\n".join(columns + constraints)
        statements.append(f"CREATE TABLE {item['table']} (\n{body}\n);")
    return "\n\n".join(statements) + "\n"


def render_html(erd: dict, mermaid: str) -> str:
    escaped = html.escape(mermaid)
    title = html.escape(erd["name"])
    entity_cards = []
    for item in erd["entities"]:
        rows = "".join(
            f"<li><code>{html.escape(f['name'])}</code><span>{html.escape(f['type'])}</span></li>"
            for f in item["fields"]
        )
        entity_cards.append(f"<section><h2>{html.escape(item['name'])}</h2><ul>{rows}</ul></section>")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{ margin: 0; font-family: Inter, Arial, sans-serif; background: #f4f6f8; color: #172033; }}
    header {{ padding: 20px 28px; background: #fff; border-bottom: 1px solid #d7dee8; }}
    main {{ display: grid; gap: 24px; padding: 28px; }}
    pre {{ overflow: auto; padding: 20px; background: #111827; color: #f9fafb; border-radius: 8px; }}
    .entities {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }}
    section {{ background: #fff; border: 1px solid #d7dee8; border-radius: 8px; padding: 16px; }}
    h1, h2 {{ margin: 0; }}
    h2 {{ font-size: 16px; }}
    ul {{ list-style: none; padding: 0; margin: 12px 0 0; display: grid; gap: 8px; }}
    li {{ display: flex; justify-content: space-between; gap: 12px; font-size: 13px; }}
    code {{ font-weight: 700; }}
  </style>
</head>
<body>
  <header><h1>{title}</h1></header>
  <main>
    <pre class="mermaid">{escaped}</pre>
    <div class="entities">{"".join(entity_cards)}</div>
  </main>
</body>
</html>
"""


def resolve_output(project: Path, value: str | None, fallback: Path) -> Path:
    path = Path(value) if value else fallback
    if not path.is_absolute():
        path = project / path
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument("--brief")
    parser.add_argument("--brief-file")
    parser.add_argument("--spec")
    parser.add_argument("--domain", choices=["finance", "commerce", "workspace", "learning", "saas"])
    parser.add_argument("--output-json")
    parser.add_argument("--output-mermaid")
    parser.add_argument("--output-sql")
    parser.add_argument("--output-html")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    context = read_context(project, args.brief_file, args.spec, args.brief)
    brief = context.get("brief", {})
    product = brief.get("product", "Product")
    domain = detect_domain(context.get("text", ""), product, args.domain)
    entities, relationships = base_entities(domain)
    add_screen_entities(entities, relationships, context.get("spec"))
    entities = dedupe_entities(entities)

    erd = {
        "name": f"{product.title()} ERD",
        "source": "llm-editable-json",
        "target_outputs": ["mermaid", "sql", "html"],
        "domain": domain,
        "brief": brief,
        "entities": entities,
        "relationships": relationships,
    }

    output_json = resolve_output(project, args.output_json, project / ".opencode/work/lunacy_erd.json")
    output_mermaid = resolve_output(project, args.output_mermaid, project / "outputs/lunacy-agent-erd.mmd")
    output_sql = resolve_output(project, args.output_sql, project / "outputs/lunacy-agent-erd.sql")
    output_html = resolve_output(project, args.output_html, project / "outputs/lunacy-agent-erd.html")
    for path in [output_json, output_mermaid, output_sql, output_html]:
        if path.exists() and not args.force:
            raise SystemExit(f"{path} already exists. Use --force to overwrite.")

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_mermaid.parent.mkdir(parents=True, exist_ok=True)
    output_sql.parent.mkdir(parents=True, exist_ok=True)
    output_html.parent.mkdir(parents=True, exist_ok=True)

    mermaid = render_mermaid(erd)
    output_json.write_text(json.dumps(erd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    output_mermaid.write_text(mermaid, encoding="utf-8")
    output_sql.write_text(render_sql(erd), encoding="utf-8")
    output_html.write_text(render_html(erd, mermaid), encoding="utf-8")
    print(f"Wrote {output_json}")
    print(f"Wrote {output_mermaid}")
    print(f"Wrote {output_sql}")
    print(f"Wrote {output_html}")


if __name__ == "__main__":
    main()
