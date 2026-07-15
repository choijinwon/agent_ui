# Lunacy Design Agent OpenCode Package

An OpenCode-style agent package for turning a product brief into editable
screen designs for Lunacy. It follows the shape of `choijinwon/agent_ppt`,
but replaces the PPT workflow with a UI/UX design workflow:

## Architecture

This package is intentionally **skills + scripts**, not skills-only.

- Skills define the agent workflow, design rules, output contracts, and when
  each step should run.
- Scripts perform deterministic generation and validation for JSON, SVG, HTML,
  React, and review artifacts.

Skills-only is not reliable enough here because SVG/HTML/React generation
requires repeatable geometry, escaping, layer IDs, and validation. The skill
layer should decide what to do; the script layer should make the artifact
consistently.

```text
.opencode/
  opencode.json
  agents/lunacy.md
  skills/
    01-lunacy-skill-brief-analyze/
    02-lunacy-skill-screen-build/
    03-lunacy-skill-svg-create/
    04-lunacy-skill-html-create/
    05-lunacy-skill-review-polish/
    06-lunacy-skill-react-export/
    07-lunacy-skill-patch-design/
  scripts/
    01-brief-analyze/
    02-screen-build/
    03-svg-create/
    04-html-create/
    05-review-polish/
    06-react-export/
    07-patch-design/
```

## Workflow

```text
1. Brief Analyze
   Reads product, audience, platform, tone, and design constraints.

2. Screen Build
   Converts the brief into a structured multi-screen UI spec with tokens,
   frames, components, assets, style presets, and copy.

3. SVG Create
   Generates a Lunacy-friendly layered SVG.

4. HTML Create
   Generates browser-ready HTML/CSS from the same screen spec.

5. React Export
   Generates a React/Tailwind-compatible `.tsx` component from the same spec.

6. Patch Design
   Applies simple instruction-driven or path-based edits to the JSON spec.

7. Review Polish
   Checks the source JSON, SVG, optional HTML, and optional React export for missing layers,
   weak contrast, oversized text blocks, and basic layout problems.
```

## Quick Start

```bash
python .opencode/scripts/01-brief-analyze/analyze_brief.py --project . --brief "AI finance dashboard for executives, dark but readable, 3 desktop screens."
python .opencode/scripts/02-screen-build/build_screens.py --project . --brief-file .opencode/work/lunacy_brief.json --screens 3 --preset fintech
python .opencode/scripts/03-svg-create/create_lunacy_svg.py --project . --spec .opencode/work/lunacy_screens.json --output outputs/lunacy-agent-sample.svg
python .opencode/scripts/04-html-create/create_html.py --project . --spec .opencode/work/lunacy_screens.json --output outputs/lunacy-agent-sample.html
python .opencode/scripts/06-react-export/export_react.py --project . --spec .opencode/work/lunacy_screens.json --output outputs/LunacyDesign.tsx
python .opencode/scripts/07-patch-design/patch_design.py --project . --spec .opencode/work/lunacy_screens.json --instruction "add modal and make it dark mode"
python .opencode/scripts/05-review-polish/review_design.py --project . --spec .opencode/work/lunacy_screens.json --svg outputs/lunacy-agent-sample.svg --html outputs/lunacy-agent-sample.html --react outputs/LunacyDesign.tsx
```

Open the generated `.svg` in Lunacy. Open the generated `.html` in a browser
to inspect the same screens as DOM/CSS. Use the generated `.tsx` in a
React/Tailwind project. Keep the `.json` next to them as the LLM-editable
source of truth.

## Added Capabilities

- Style presets: `saas`, `fintech`, `mobile-native`, `ecommerce`, `admin`,
  and `dark`.
- Asset metadata: inline icon names and image placeholder records under
  `assets`.
- Expanded components: modal, table, tabs, dropdown, form, toast, pricing
  card, calendar, kanban board, and image placeholder.
- React/Tailwind export: `outputs/LunacyDesign.tsx`.
- Patch loop: natural-language edits and exact JSON path edits.

```bash
python .opencode/scripts/07-patch-design/patch_design.py --project . --spec .opencode/work/lunacy_screens.json --set frames.0.components.1.text="New headline"
```

## Why SVG

Lunacy supports professional UI design workflows, imports from Figma, and
converts Figma files to `.sketch`. For LLM-generated design, this package uses
SVG because it is readable, editable, diffable, and can be imported into vector
design tools as layered shapes instead of a flat bitmap.

## Principles

- The agent creates or edits only design artifacts: JSON specs, SVG files, and
  HTML/CSS or React previews.
- Source files from the user are not overwritten.
- Existing output files are overwritten only with `--force`.
- Secrets such as API keys, tokens, and passwords are never printed.
