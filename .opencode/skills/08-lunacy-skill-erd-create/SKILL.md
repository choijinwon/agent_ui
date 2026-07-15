# ERD Create

Use this skill when the user asks for an ERD, entity relationship diagram,
database model, schema, Mermaid ERD, SQL DDL, or data model for a generated UI
or product brief.

## Goal

Create a data-model layer for the UI design package:

- `.opencode/work/lunacy_erd.json`
- `outputs/lunacy-agent-erd.mmd`
- `outputs/lunacy-agent-erd.sql`
- `outputs/lunacy-agent-erd.html`

## Workflow

1. Read `.opencode/work/lunacy_screens.json` when it exists.
2. Fall back to `.opencode/work/lunacy_brief.json` or a direct brief.
3. Detect the domain: `finance`, `commerce`, `workspace`, `learning`, or
   `saas`.
4. Generate entities, fields, primary keys, foreign keys, and relationships.
5. Export Mermaid ERD, SQL DDL, and a standalone HTML preview.
6. Review that relationships point to existing entities.

## Command

```bash
python .opencode/scripts/08-erd-create/create_erd.py --project . --spec .opencode/work/lunacy_screens.json --force
```

Optional domain override:

```bash
python .opencode/scripts/08-erd-create/create_erd.py --project . --brief-file .opencode/work/lunacy_brief.json --domain finance --force
```

## Modeling Rules

- Use singular entity names: `User`, `Account`, `Transaction`.
- Use snake_case table and field names.
- Always include stable `id` primary keys.
- Add timestamps where lifecycle matters.
- Prefer explicit join entities over hidden many-to-many relationships.
- Keep UI-only state out of the ERD unless it represents persisted data.
- If the UI contains settings screens, add a `Preference` entity.
- If the UI contains notifications or alerts, add a `Notification` entity.

## Output Schema

```json
{
  "name": "Product ERD",
  "source": "llm-editable-json",
  "target_outputs": ["mermaid", "sql", "html"],
  "domain": "finance",
  "brief": {},
  "entities": [
    {
      "name": "User",
      "table": "user",
      "fields": [
        {
          "name": "id",
          "type": "uuid",
          "required": true,
          "primary_key": true
        }
      ]
    }
  ],
  "relationships": [
    {
      "left": "User",
      "right": "Account",
      "cardinality": "one-to-many",
      "label": "owns"
    }
  ]
}
```
