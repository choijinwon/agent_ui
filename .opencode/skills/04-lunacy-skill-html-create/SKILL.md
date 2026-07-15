# HTML Create

Use this skill after screen spec creation when the user wants browser-ready
HTML output, an inspectable preview, or code that can be handed to frontend
implementation.

## Goal

Generate a standalone HTML/CSS file from `.opencode/work/lunacy_screens.json`.
The HTML should represent the same screens as the Lunacy SVG, but as DOM nodes
instead of a flat image.

## Procedure

1. Read `.opencode/work/lunacy_screens.json`.
2. Convert frames into `.screen-frame` sections.
3. Convert components into semantic HTML where practical:
   - buttons become `<button>`
   - search becomes `<label>` and `<input>`
   - navigation becomes `<nav>`
   - charts remain lightweight HTML/CSS/SVG hybrids
4. Preserve each component ID with `data-layer-id`.
5. Run:

```bash
python .opencode/scripts/04-html-create/create_html.py --project . --spec .opencode/work/lunacy_screens.json --output outputs/design.html
```

## Output

A standalone HTML file in `outputs/`.
