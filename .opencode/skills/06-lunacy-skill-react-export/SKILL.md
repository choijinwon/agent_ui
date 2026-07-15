# React Export

Use this skill when the user wants implementation-oriented output from the
same UI design spec.

## Goal

Generate a standalone React/Tailwind-compatible `.tsx` component from
`.opencode/work/lunacy_screens.json`.

## Procedure

1. Read `.opencode/work/lunacy_screens.json`.
2. Preserve design tokens as CSS custom properties on the root element.
3. Convert frames into positioned React sections.
4. Convert known components into semantic JSX where practical.
5. Run:

```bash
python .opencode/scripts/06-react-export/export_react.py --project . --spec .opencode/work/lunacy_screens.json --output outputs/LunacyDesign.tsx
```

## Output

A `.tsx` file in `outputs/`.
