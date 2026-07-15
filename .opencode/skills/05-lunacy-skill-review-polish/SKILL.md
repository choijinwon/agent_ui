# Review Polish

Use this skill after SVG, HTML, optional React, and optional ERD creation.

## Goal

Review the generated design artifacts before handoff.

## Procedure

1. Check that the spec and SVG exist.
2. Check that optional HTML, React, and ERD files exist when requested.
3. Check that every screen has a frame title and components.
4. Check that every component has a unique ID.
5. Check approximate text fit and contrast.
6. Check that the SVG is valid XML.
7. Check that HTML contains screen frames and layer IDs.
8. Check that React exports a component and preserves layer IDs.
9. Check that ERD JSON has entities, primary keys, and valid relationships.
10. Run:

```bash
python .opencode/scripts/05-review-polish/review_design.py --project . --spec .opencode/work/lunacy_screens.json --svg outputs/design.svg --html outputs/design.html --react outputs/LunacyDesign.tsx --erd-json .opencode/work/lunacy_erd.json --erd-mermaid outputs/lunacy-agent-erd.mmd --erd-sql outputs/lunacy-agent-erd.sql
```

## Output

`.opencode/work/lunacy_review.json`
