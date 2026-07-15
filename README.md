# Lunacy Design Agent OpenCode Package

An OpenCode-style agent package for turning a product brief into editable
screen designs for Lunacy. It follows the shape of `choijinwon/agent_ppt`,
but replaces the PPT workflow with a UI/UX design workflow:

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
  scripts/
    01-brief-analyze/
    02-screen-build/
    03-svg-create/
    04-html-create/
    05-review-polish/
```

## Workflow

```text
1. Brief Analyze
   Reads product, audience, platform, tone, and design constraints.

2. Screen Build
   Converts the brief into a structured multi-screen UI spec with tokens,
   frames, components, and copy.

3. SVG Create
   Generates a Lunacy-friendly layered SVG.

4. HTML Create
   Generates browser-ready HTML/CSS from the same screen spec.

5. Review Polish
   Checks the source JSON, SVG, and optional HTML for missing layers,
   weak contrast, oversized text blocks, and basic layout problems.
```

## Quick Start

```bash
python .opencode/scripts/01-brief-analyze/analyze_brief.py --project . --brief "AI finance dashboard for executives, dark but readable, 3 desktop screens."
python .opencode/scripts/02-screen-build/build_screens.py --project . --brief-file .opencode/work/lunacy_brief.json --screens 3
python .opencode/scripts/03-svg-create/create_lunacy_svg.py --project . --spec .opencode/work/lunacy_screens.json --output outputs/lunacy-agent-sample.svg
python .opencode/scripts/04-html-create/create_html.py --project . --spec .opencode/work/lunacy_screens.json --output outputs/lunacy-agent-sample.html
python .opencode/scripts/05-review-polish/review_design.py --project . --spec .opencode/work/lunacy_screens.json --svg outputs/lunacy-agent-sample.svg --html outputs/lunacy-agent-sample.html
```

Open the generated `.svg` in Lunacy. Open the generated `.html` in a browser
to inspect the same screens as DOM/CSS. Keep the `.json` next to them as the
LLM-editable source of truth.

## Why SVG

Lunacy supports professional UI design workflows, imports from Figma, and
converts Figma files to `.sketch`. For LLM-generated design, this package uses
SVG because it is readable, editable, diffable, and can be imported into vector
design tools as layered shapes instead of a flat bitmap.

## Principles

- The agent creates or edits only design artifacts: JSON specs, SVG files, and
  HTML/CSS previews.
- Source files from the user are not overwritten.
- Existing output files are overwritten only with `--force`.
- Secrets such as API keys, tokens, and passwords are never printed.
