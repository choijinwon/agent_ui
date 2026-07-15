# SVG Create

Use this skill after screen spec creation.

## Goal

Generate a layered SVG that can be opened in Lunacy and inspected as vector
design content.

## Procedure

1. Read `.opencode/work/lunacy_screens.json`.
2. Convert frames into artboard-like SVG groups.
3. Convert components into grouped vector layers.
4. Preserve IDs and names from the JSON spec.
5. Optionally create an HTML preview next to the SVG.
6. Run:

```bash
python .opencode/scripts/03-svg-create/create_lunacy_svg.py --project . --spec .opencode/work/lunacy_screens.json --output outputs/design.svg --html outputs/design.html
```

## Output

An SVG file in `outputs/`, plus optional preview HTML.
