---
name: dpip-asset-mapping
description: Use in the Design-Pipeline (dpip) workflow when a DTCG token spec and visual-observations matrix must be mapped into a lightweight, selective reusable-asset plan for Penpot. Clusters components into families without overproducing variants and produces an asset-plan JSON consumed by dpip-penpot-assets. Front-load keywords: dpip, design pipeline, asset mapping, asset plan, assets, variants, button, input, card.
---

# Asset Mapping

Turn a `dpip-design-tokens` spec into a reusable-asset plan for Penpot. This is the analysis /
grouping stage — platform-agnostic, no Penpot here. It does not know Penpot's current
state, so it does not flag name collisions against existing assets; that detection happens
in `dpip-penpot-assets`.

## Manifest lineage

This skill is an operational derivative of the human requirements in
`C:\dev\direct-import\human-manifests\dpip-manifest.md` version `0.2`, interpreted through
`C:\dev\direct-import\dpip\README.md` and constrained by
`C:\dev\direct-import\dpip\core-guardrails.md` and `contract.json`.

It must preserve the distinction between complete observation and selective asset creation,
human authority over uncertain family interpretations, evidence-based variants, and the
non-invention of unsupported combinations. Reports and historical artefacts are evidence only.

The exact Manifest version for this plan must be recorded in its run metadata. Do not use an
unqualified "latest" reference for execution or replay. A later Manifest version requires impact
review before this skill is used for new plans.

The universal invariants live in `C:\dev\direct-import\dpip\core-guardrails.md`. This skill owns
only source-derived asset decisions. Do not duplicate the core mutation rules here.

The executable reference implementation is `C:\dev\direct-import\dpip\compile_assets.py`.
For selective asset planning, use the compiler; the agent reports and validates its output but
must not synthesize an alternative plan by free-form reasoning.

Pipeline position:

```
dpip-design-tokens (DTCG spec) -> dpip-asset-mapping (asset plan) -> dpip-penpot-assets (Penpot)
```

## Restate the brief as a contract

- **Context** — the token spec file + any observations document it was derived from.
- **Objective** — one goal: an asset plan that groups reusable controls into the smallest
  sensible set of assets, while keeping complete observations separate from selective import.
- **Inputs** — the spec's `tokens` (component layer), `usage` manifest, and (optional)
  the source `observations.json` (`components` array) for geometry/layout hints.
- **Constraints** — one asset per control *type*; variants express stable semantic or
  behavioural axes; interchangeable controls merge into one asset; reusable icon treatments
  are separate assets with their own variants; content and concrete icon choice are slots or
  sub-asset properties; placement axes such as `IconPosition` are open and evidence-derived;
  no invented values (mark gaps instead).
- **Layout constraint** — derive `layout.axis`, `width.behavior`, and `height.behavior` from
  observations. Do not replace dynamic behaviour with a measured screenshot width or height.
- **Acceptance criteria** — every planned component-layer token has an explicit usage and
  resolves to the intended asset/property; a token may be reused by multiple variants; every
  observed item is classified or explicitly skipped; every asset has >= 1 variant; every
  variant has distinct property values; no silent omissions; every planned mutation has one
  deterministic identity and occurs once.

The asset plan is a declarative contract, not a complete desired-state snapshot. It records what
the current evidence approves; Penpot remains authoritative for what already exists.

Act as a senior design-systems engineer. Record a justified reason for every grouping.

## Inputs

| Input | Read with | Provides |
| ----- | --------- | -------- |
| Token spec (DTCG) | `read` | `tokens` (component layer), `usage` (`component`, `property`, `states`, `variants`, `theme`) |
| Observations doc | `read` | per-component `components` entries: `role`, `where`, size, layout, text |

The `usage` manifest is the primary grouping source — its `component` (PascalCase) and
`variants` fields name the controls and their observed configurations. The observations
doc adds geometry (size) and layout that the token spec does not carry.

## Grouping rules

1. **Same type -> one asset, variants only for stable differences.** Controls that share a
   `component` name (Button, Card, Input, …) become ONE asset where appropriate. Size,
   hierarchy, evidenced state, and observed placement relationships may be axes; label,
   screenshot position, free width, and raster noise are slots/properties or layout details,
   not axes.
2. **Reusable icon -> separate asset.** Reused or alternative icon treatments are separate
   assets (for example `ButtonIcon`) with their own open `Icon` property. A parent composes
   that asset through an optional icon slot; it must not duplicate icon geometry.
3. **Placement axis -> open, evidence-derived property.** `IconPosition` has no hardcoded
   enum. Derive values from the source (`Leading`, `Trailing`, `Top`, `Bottom`, `Overlay`, or
   any other observed value). `None` is a universally valid reserved absence value, but a
   `None` variant is created only when observations or asset policy approve it.
4. **Interchangeable -> one asset, a `Type` axis.** Controls used at the same hierarchy
   level and swappable in the UI (text-field vs dropdown; checkbox vs switch) merge into
   one asset whose first variant axis is `Type`.
5. **Distinct type & distinct use -> separate assets.** Do not merge controls that are
   never swapped for each other (e.g. a Button and a Navbar).
6. **One variant = one distinct property-value combination.** Two variants must not share
   the same value on every axis; a duplicate combination is a grouping error.
7. **Variant axes are ordered.** Put the most discriminating axis first (`Type`, then
   `Hierarchy`, then `Size`, then `State`); Penpot uses this order for the swap UI.
8. **One logical asset has one declared destination.** Every planned variant must point to
   exactly one parent asset and exactly one final VariantContainer. A variant intended for a
   parent must never be planned as a second standalone asset.
9. **Exactly-once mutation identity.** Emit a deterministic mutation key for every planned
   create, bind, compose, and group operation. Duplicate keys, duplicate variant tuples, or
   ambiguous destinations invalidate the plan before Penpot is touched.

## Output: asset-plan JSON

Emit one document (this is the contract `dpip-penpot-assets` consumes):

```json
{
  "meta": {
    "schemaVersion": "1.0",
    "planVersion": "1.0",
    "mode": "additive",
    "sourceSpec": "<path to token spec>",
    "sourceObservations": "<path or null>",
    "sourceFingerprint": "<canonical source fingerprint>",
    "processedAt": "ISO-8601",
    "confidence": 0.0..1.0
  },
  "assets": [
     {
       "name": "Button",
       "assetKey": "button",
       "grouping": "variants",
       "properties": ["Hierarchy", "Size", "IconPosition"],
       "propertyValues": {
         "IconPosition": ["<values-derived-from-source>"]
       },
       "policy": {
         "mode": "additive",
         "requiresReviewFor": []
       },
       "layout": {
         "axis": "horizontal",
         "width": "content-dependent",
         "height": "fixed"
       },
       "variants": [
         {
           "id": "button.primary.desktop",
           "variantKey": "Hierarchy=Primary|Size=Desktop|IconPosition=<value-derived-from-source>",
            "properties": { "Hierarchy": "Primary", "Size": "Desktop", "IconPosition": "<value-derived-from-source>" },
          "bindings": [
            { "property": "fill", "token": "button.primary.bg" },
            { "property": "borderRadius", "token": "button.radius" },
            { "property": "fontSize", "token": "button.primary.text.size" }
          ],
           "slots": [
             { "name": "label", "text": "Button", "typography": "button.primary.text" },
             {
               "name": "icon",
               "asset": "ButtonIcon",
               "variantProperty": "Icon",
               "positionProperty": "IconPosition",
               "optional": true
             }
           ],
          "geometry": { "width": 96, "height": 40 },
           "layout": {
             "axis": "horizontal",
             "width": "content-dependent",
             "height": "fixed"
           }
        }
      ]
    }
  ],
  "gaps": [
    { "asset": "Button", "reason": "no observed height for the shortened variant" }
  ]
}
```

Field contracts:

- `name` — PascalCase component name (becomes the Penpot component name).
- `assetKey` — stable family identity; it must not contain a run number or temporary version
  suffix.
- `grouping` — `"variants"` (same type, different axes) or `"interchangeable"` (merged
  controls; `properties[0]` MUST be `"Type"`).
- `properties` — ordered variant-axis names (become `Variants.properties` in Penpot).
- `propertyValues` — optional, per-asset values copied from the current observations or an
  explicit approval. The values are dynamic output, not a global enum; never copy the example
  placeholders or impose a fixed list. `None` is the reserved valid absence value for an
  optional icon slot.
- `variants[].properties` — one value per axis, in `properties` order.
- `variants[].id` — stable unique identity for the variant. It must be unique within the plan;
  the canonical tuple of ordered property values must also be unique within its parent asset.
- `variants[].variantKey` — canonical, ordered property tuple used for reconciliation. It is
  the identity of the variant; display names are not.
- `variants[].bindings` — mandatory token bindings for every governed visual property of this
  variant; `property` is a shape/token property (see `dpip-penpot-assets`), `token` a dot-separated
  token path. An empty binding list is valid only when the plan records an explicit unresolved
  gap and blocks the write stage for that property.
- `variants[].slots` — named content regions (label, icon, placeholder); carry a sample
  `text` and, where relevant, a `typography` token. A reusable slot may include `asset`,
  `variantProperty`, `positionProperty`, and `optional` to describe composition.
- `variants[].geometry` / `layout` — optional size/layout hints from observations.
- `layout` — optional behaviour summary: `axis` is source-derived; each dimension is
  `fixed`, `content-dependent`, `fill-available`, or `unknown`. A behaviour summary is not a
  hardcoded pixel value.
- `gaps` — anything unreadable; do NOT invent values to fill them.

- `policy` — optional asset-specific delta only (`mode`, review requirements, or family-specific
  composition). It must not restate the universal guardrails.

For the write stage, the plan may additionally carry a deterministic `mutationKey` per asset,
variant, binding, composition, and final grouping operation. These keys are execution identities,
not Penpot layer names.

Every token in `layers.components` must have an explicit usage in the asset plan's `bindings`
or `slots`. Reuse across variants is valid; a token referenced nowhere is a mapping gap.

Before handing the plan to `dpip-penpot-assets`, validate that every variant tuple is unique,
every composed child has one declared parent slot, every parent has one final container, and
no planned logical variant exists both as a standalone asset and as a parent variant.
Also validate that each non-unknown sizing behaviour has evidence or an approved token, and
that `unknown` layout behaviour is surfaced as a review gap rather than silently resolved.

## Observation-to-import gate

Read `variantMatrix` from the observations document when present, but do not translate it
one-to-one into Penpot assets. Classify every observation as a canonical component,
existing-component instance, local pattern, decorative element, or unresolved finding.
Every observation needs a classification or explicit skip; only canonical components and
approved stable axes become planned variants. Open placement axes are derived per asset from
evidence; do not constrain them to a shared enum or generate unobserved combinations.
Keep the review lightweight: escalate only family-level ambiguity, more than three public
axes, or more than twelve automatic combinations per asset.

## Workflow

1. **Read the spec.** Load `tokens`, `layers.components`, and `usage`.
2. **Group** by the rules above; produce the asset list and variant axes. Name each axis
   and justify each merge in the report.
3. **Bind tokens** — for each variant, list the component-layer tokens it consumes
   (`fill`, `borderRadius`, `typography`, `spacing`, `opacity`, …).
4. **Fill geometry/slots** from the observations doc where available; mark gaps otherwise.
5. **Validate** against the checklist; run the confidence gate below.

## Confidence gate

If `meta.confidence` < 0.8, or a high proportion of `gaps`/`approx` values, stop and
require human review before treating the plan as final.

## Validation checklist (acceptance gates)

- [ ] Every planned component-layer token has an explicit usage; reuse across variants is
      allowed and intentional.
- [ ] Every observed item is classified or explicitly skipped with a reason.
- [ ] Every asset has >= 1 variant; variant property values are pairwise distinct.
- [ ] `grouping: "interchangeable"` assets have `Type` as the first axis.
- [ ] `properties` and each `variants[].properties` use the same ordered axes.
- [ ] Every variant tuple is unique within its parent asset; every logical parent variant has
      exactly one declared destination container.
- [ ] Mutation identities are deterministic and unique; no parent variant is also planned as a
      standalone asset.
- [ ] No invented geometry/typography values — gaps recorded instead.
- [ ] Every multi-child asset has a source-derived Flex/Grid layout requirement; layout-less
      construction is not an acceptable downstream implementation.
- [ ] `meta.schemaVersion` present and confidence gate passed.
- [ ] Observation and import counts are reported separately and are consistent.

## Report

End with: assets and variant counts, grouping decisions (what was merged and why), token
coverage (all component tokens bound / which are gaps), `meta.confidence`, and anything
needing human review.
