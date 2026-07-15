# Screen Build

Use this skill after brief analysis.

## Goal

Create an LLM-editable UI design spec at `.opencode/work/lunacy_screens.json`.

## Procedure

1. Read `.opencode/work/lunacy_brief.json`.
2. Decide the artboard size from platform.
3. Define tokens before components:
   - colors
   - typography
   - spacing
   - radius
4. Create one frame per screen.
5. Give every component a stable ID, role, x/y/w/h, text, and style reference.
6. Run:

```bash
python .opencode/scripts/02-screen-build/build_screens.py --project . --brief-file .opencode/work/lunacy_brief.json --screens 3
```

## Output

`.opencode/work/lunacy_screens.json`
