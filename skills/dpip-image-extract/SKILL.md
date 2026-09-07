---
name: dpip-image-extract
description: Use when a PNG, JPG, WebP, SVG, or other visual source must be analysed into complete visual observations for downstream design-token and asset workflows. Always inventory every observed component type, variant axis, state, icon treatment, and evidence region; never silently sample only representative variants.
---

# Image Extract

This is the vision stage of the design-token and asset pipeline. It consumes visual
sources and writes a structured `visual-observations` document for text-only stages.

For raster sources, the run must carry an explicit human `assetGeneration` decision before
processing: `tokens-only`, `plan-only`, or `approved-assets`. The decision applies to all observed
families by default and may include explicit family overrides. Never infer asset creation from the
image, and never inherit the decision from a historical run.

## Manifest lineage

This skill is an operational derivative of the human requirements in
`C:\dev\direct-import\human-manifests\dpip-manifest.md` version `0.2`, interpreted through
`C:\dev\direct-import\dpip\README.md`.

Its observations are evidence for human-controlled downstream decisions. It must preserve
source-dependent uncertainty and must not silently turn missing semantic or interaction evidence
into asserted component structure. Reports and observation artefacts are evidence, not new
requirements.

Record the exact Manifest version used for the observation run. Do not use an unqualified "latest"
reference for execution or replay; later Manifest versions require impact review before new
observations are used downstream.

## Output contract

The document MUST contain `meta`, `palette`, `typography`, `spacing`, `radius`,
`elevation`, `opacity`, `layout`, `components`, `variantMatrix`, `text`,
`uncertainties`, and `gaps`.

Every observed component entry MUST include a stable name, role, evidence region(s),
all observed variant axes, every observed combination of axis values, confidence, and
`approx` markers for estimates. Where the source supports it, record layout direction and
sizing behaviour separately from raw geometry.

## Completeness rules

1. Do not reduce a state matrix to a `variantsObserved` list only.
2. Do not emit only default or representative variants unless the document explicitly
   declares `coverageMode: "sampled"` and records every omitted observation as a gap.
3. The default mode is `coverageMode: "complete-observation"`.
4. Every visual region containing a reusable control must appear in `variantMatrix`
   or be recorded in `gaps` with a reason.
5. State-specific fills, labels, strokes, icon treatment, opacity, borders, and loading,
   selected, or disabled clues must be recorded separately where visible.
6. Keep `observed`, `interpreted`, and `unknown` separate.

## Evidence format

Each variant should resemble:

```json
{
  "id": "button.primary.desktop.default.with-arrow",
  "component": "Button",
  "properties": { "Type": "Primary", "Size": "Desktop", "State": "Default", "Icon": "WithArrow" },
  "evidence": [{ "region": { "x": 0, "y": 0, "width": 100, "height": 40 }, "source": "image" }],
  "observed": { "fill": "#E52B21", "label": "Button", "arrow": "right-chevron" },
  "layout": {
    "axis": "horizontal",
    "width": { "behavior": "content-dependent", "evidence": ["region-1"], "confidence": 0.84 },
    "height": { "behavior": "fixed", "evidence": ["region-1"], "confidence": 0.89 }
  },
  "confidence": 0.94,
  "approx": false
}
```

Coordinates may be normalized, but source dimensions and coordinate system must be
recorded. Do not claim CSS/Penpot units where only raster pixels are available.

## Layout and sizing inference

Record behaviour, not just screenshot dimensions:

- `layout.axis` — observed content/layout flow, normally `horizontal`, `vertical`, or
  `unknown`; do not infer a value from a single ambiguous crop.
- `width.behavior` and `height.behavior` — `fixed`, `content-dependent`, `fill-available`, or
  `unknown`.
- Every inferred behaviour needs evidence regions and confidence.
- Compare multiple instances or text lengths when deciding whether a dimension is fixed or
  content-dependent. A single measured width is geometry, not proof of fixed sizing.
- For text, distinguish one-dimensional content growth from wrapping: a constrained multiline
  text box may have fixed width and content-dependent height even when its layout flow is
  horizontal.
- Keep the raw measured geometry as evidence, but do not promote it to a hardcoded asset
  dimension without a token or a confirmed sizing behaviour.

## Completion gate

Return component-type count, observed-variant count, state/size/icon counts,
observed-region coverage, omitted or ambiguous variants, confidence, and limitations.
The document is incomplete if a visible component or state is missing without a gap.
