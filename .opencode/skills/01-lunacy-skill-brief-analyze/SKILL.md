# Brief Analyze

Use this skill when a user asks for a screen design, app design, dashboard,
wireframe, or Lunacy/Figma-like UI artifact.

## Goal

Convert a natural-language request into `.opencode/work/lunacy_brief.json`.

## Procedure

1. Preserve the user's exact brief.
2. Extract product type, audience, platform, style, required screens, and
   must-have content.
3. Prefer the user's constraints over defaults.
4. If details are missing, choose conservative UI defaults:
   - platform: desktop
   - style: clean, focused, professional
   - screens: overview, detail, settings
5. Run:

```bash
python .opencode/scripts/01-brief-analyze/analyze_brief.py --project . --brief "<brief>"
```

## Output

`.opencode/work/lunacy_brief.json`
