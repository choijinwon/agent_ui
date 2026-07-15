# Patch Design

Use this skill when the user wants to iterate on an existing generated design,
for example "make it dark", "add a modal", "add a table", or "change this text".

## Goal

Modify `.opencode/work/lunacy_screens.json` without rebuilding the design from
scratch.

## Procedure

1. Read the current design spec.
2. Apply a natural-language patch when possible.
3. Use `--set path=value` for exact edits.
4. Regenerate SVG, HTML, and React outputs after patching.
5. Review artifacts.

```bash
python .opencode/scripts/07-patch-design/patch_design.py --project . --spec .opencode/work/lunacy_screens.json --instruction "add modal and make it dark mode"
python .opencode/scripts/07-patch-design/patch_design.py --project . --spec .opencode/work/lunacy_screens.json --set frames.0.components.1.text="New headline"
```

## Output

An updated JSON design spec.
