---
name: dpip-penpot-assets
description: Use in the Design-Pipeline (dpip) workflow when a selective asset plan from dpip-asset-mapping must be written into Penpot as token-bound library components and variants. Builds editable Flex/Grid structures and verifies observation/import coverage without object explosion. Front-load keywords: dpip, design pipeline, penpot assets, components, variants, button, input, card.
---

# Penpot Assets (write)

Write a `dpip-asset-mapping` asset plan into Penpot as library components with variants, via
the Penpot MCP. This is the write stage — the only one that talks to Penpot for assets.

For raster-source runs, this stage is permitted only when the run metadata selects
`assetGeneration.decision: "approved-assets"` (or an approved family override) and records a
human `approvalId`. `tokens-only` and `plan-only` runs must stop before Penpot asset mutation.

## Manifest lineage

This skill is an operational derivative of the human requirements in
`C:\dev\direct-import\human-manifests\dpip-manifest.md` version `0.4`, interpreted through
`C:\dev\direct-import\dpip\README.md` and constrained by
`C:\dev\direct-import\dpip\core-guardrails.md` and `contract.json`.

Penpot mutations must preserve human approval, additive-by-default updates, source-dependent
confidence, evidence-based variants, persisted token bindings, and the requirement that failed
postconditions stop the affected flow. Platform/API constraints must remain identifiable as
technical constraints rather than being presented as human requirements.

The exact Manifest version for the write run must be recorded in the run ledger and mutation
manifest. Do not use an unqualified "latest" reference. Existing runs and historical plans remain
tied to their recorded Manifest version; a later version requires impact review before writing.

Universal safety rules live in `C:\dev\direct-import\dpip\core-guardrails.md`. This skill
executes the asset plan and reconciles it with Penpot; it does not invent family decisions.

Asset plans for `create`/extract are produced by `C:\dev\direct-import\dpip\compile_assets.py`.
This write skill consumes and validates that plan; it does not regenerate a competing plan.

Pipeline position:

```
dpip-design-tokens -> dpip-asset-mapping (asset plan) -> dpip-penpot-assets (Penpot components)
```

## Preconditions

- Penpot project connected to the MCP server (Penpot MCP Plugin).
- Token sets already imported by `dpip-penpot-tokens` and **active** (bindings need the
  referenced sets active, or `resolvedValue` is undefined).
- Call `high_level_overview` once before any Penpot action.
- Input: the asset-plan JSON (`assets`, each with `properties` and `variants`).

## Restate the brief

- **Context** — the asset plan + the connected file's current component/token state.
- **Objective** — every approved asset in the plan exists in Penpot as a component with its
  planned variants, bound to the right tokens. Observations classified as instances, local
  patterns, decorative elements, or unresolved findings are not forced into library assets.
- **Inputs** — `assets[].name`, `properties`, `variants[]` (`properties`, `bindings`,
  `slots`, `geometry`, `layout`).
- **Composition** — create reusable sub-assets (such as `ButtonIcon`) before parent assets;
  parent slots reference the sub-asset and its own variant property rather than copying its
  geometry.
- **Layout** — implement the plan's observed flow and sizing behaviour with editable Penpot
  flex/text structure. Do not turn a measured screenshot dimension into a fixed size unless the
  plan marks it `fixed` and supplies evidence or a token.
- **Constraints** — exactly-once mutations (no duplicate creates, bindings, compositions, or
  groupings); token bindings resolve; one main component per planned variant; no logical parent
  variant may remain outside its declared final VariantContainer.
- **Acceptance criteria** — each approved asset is a `VariantContainer` with one component
  per planned variant; every binding's token resolves; every observation is classified or
  explicitly skipped; visual review passes; the mutation manifest has no duplicate identities
  and every planned mutation has a recorded single outcome; every governed property has a
  persisted `shape.tokens` binding after component creation; every multi-child container uses
  Flex or Grid.
- **Mode** — default `additive`; `design-system-change` must be explicit in the plan and run.

### Confidence review payloads

Assets with `requiresReview=true` may contain a deterministic `reviewAnnotation` payload generated
by `compile_assets.py`. Preserve that payload alongside the asset identity and run ledger. Before
writing an actual Penpot annotation, verify the connected API signature; do not guess an annotation
method or mutate a shape through an undocumented property. If the API does not expose annotations,
the run must retain the payload in the plan/ledger and report `annotationUnsupported` rather than
silently discarding the review information.

## Building a variant's shapes

Construct each variant's geometry, establish Flex/Grid layout, then bind tokens. Basic surface
with label:

```js
const board = penpot.createBoard();
const flex = board.addFlexLayout();       // use Grid for repeated/aligned matrices
flex.dir = "row";
// Apply layout.axis and width/height.behavior first. Only confirmed fixed dimensions
// may be assigned from geometry; dynamic dimensions must use editable flex/text behaviour.
const label = penpot.createText(slot.text || "Label");
board.appendChild(label);                 // append order controls Flex order
// Surface fills, strokes, spacing, and typography are all applied with tokens below.
```

### Layout and sizing behaviour

Apply the asset plan's layout summary before choosing fixed geometry:

- `axis=horizontal` or `axis=vertical` describes the content/layout flow and should map to an
  editable flex direction where supported.
- `fixed` dimensions use a resolved token or confirmed source value.
- `content-dependent` dimensions use editable hug-content/text growth behaviour; do not assign a
  screenshot width or height merely because it was measured.
- `fill-available` uses the available parent dimension.
- `unknown` stops the affected write or remains an explicit review gap; it is never guessed.
- For text, preserve constrained multiline behaviour: fixed width with content-dependent height
  is valid even when the flow is horizontal.

For content-dependent, content-bearing assets, explicitly set Penpot fit-content sizing:

- horizontal growth: `horizontalSizing = "auto"`;
- vertical growth: `verticalSizing = "auto"`.

Do not apply fit-content to every dynamic asset. If the asset plan says `fill-available`, use
Penpot fill sizing (`horizontalSizing = "fill"` or `verticalSizing = "fill"`); if it says
`fixed`, retain fixed sizing. The plan's width/height behaviour is authoritative.

When a fixed width or height is detected, use Penpot fixed sizing (`fix`) and configure the
corresponding dimension. This applies equally to horizontally oriented assets; flow direction
does not turn a fixed width into fit-content.

The A1 Design documented Button minimum width (`140px`) is globally descoped from imports by
explicit user decision. Preserve it as deferred evidence, but do not emit, bind, or enforce it
during import. Re-enable it only in an explicit `design-system-change` run with a tested Penpot
structure.

When the API exposes grow/resize behaviour, verify the resulting postcondition after applying it.
If the API does not support the requested behaviour, record `unsupported` instead of silently
falling back to a static dimension.

Bindings use `shape.applyToken(token, properties)`; resolve tokens by name first. `Token`
targets `TokenProperty` values — `"fill"` for colors, `"borderRadiusTopLeft".."borderRadiusBottomLeft"`
for radius (or `"all"`), `"fontSize"`/`"fontFamilies"`/`"fontWeight"` for text,
`"rowGap"`/`"columnGap"`/`"paddingLeft"`.. for spacing, `"opacity"` for opacity:

```js
const tok = penpotUtils.findTokenByName(binding.token);
if (!tok) throw new Error(`token not found: ${binding.token}`);
box.applyToken(tok, [binding.property]);   // e.g. ["fill"], ["borderRadiusTopLeft", ...]
```

Applying tokens is asynchronous; wait ~100ms before validating. The resolved value lands
on the shape property; `shape.tokens` records the binding.

### Binding gate — mandatory

After `createComponent`, read the final main and all descendants again. For every governed
property, require both a resolved visual value and a matching entry in `shape.tokens`. Matching
the resolved color, font, spacing, or border by direct assignment is not a binding. If token
application fails, stop and fix the binding or propose the missing semantic token; never fall
back to the literal value. The final asset must report:

```text
direct governed values: 0
missing persisted bindings: 0
containers without Flex/Grid: 0
```

## Workflow

**Phase 0 — Discover.** `high_level_overview`; read the asset plan; list existing
components (`penpot.library.local.components`) and tokens (`penpotUtils.tokenOverview()`).
✋ Checkpoint: reconcile by `assetKey` and `variantKey` metadata before falling back to display
 names. In additive mode, any incompatible existing identity is a conflict. Reuse and creation of
 approved missing objects are permitted only after the applicable human review checkpoint; they
 are not unrestricted automatic or Auto-fix actions.

Before any mutation, compile a run-scoped mutation manifest. Each record must contain a stable
`mutationId`, target asset, operation, and expected outcome. The manifest must contain exactly
one record for each planned component creation, token binding, composition, and final grouping.
Reject the plan before writing if any mutation ID, target/operation pair, variant tuple, or final
container is duplicated. A timeout or unknown result is not permission to retry: re-read Penpot,
reconcile the mutation ledger, and stop if the outcome cannot be established.

Derive the complete identity map before writing. Names and layer positions are presentation, not
identity. Store the asset and variant identities in Penpot metadata when the API supports it.
Persist `RUN_ID`, source fingerprint, plan version, and Penpot baseline in the run ledger before
the first write; session storage may cache this information but cannot be its authority.

**Phase 1 — Build one variant, bind tokens.** Build shapes for the first variant, bind its
`bindings`/`slots`, then `export_shape` the result and look at it yourself. Fix visible
issues (overlap, clipping, wrong fill, missing border, or missing layout) before proceeding. ✋ Checkpoint: approve the first
variant's look.

### Composable icon assets

When an asset plan contains a reusable icon slot:

1. Build and validate the referenced icon asset first as its own VariantContainer. Its `Icon`
   values come from source observations; the skill must not impose a fixed icon enum.
2. Build the parent asset with the placement property named by the plan (for buttons this is
   commonly `IconPosition`). The axis is open: copy only values observed or explicitly
   approved for that asset. Do not reject values such as `Top`, `Bottom`, or `Overlay` merely
   because they are not in an internal list.
3. Treat `IconPosition=None` as a reserved valid absence value. It means no icon slot at all,
   not an empty placeholder. Create it only when observed or when the asset policy explicitly
   approves the optional no-icon baseline.
4. Insert the sub-asset as a real component instance. For `Leading`/`Trailing`-style values,
   validate both visual position and child order; for new values derive the layout relationship
   from the evidence instead of guessing.

The asset plan may expose observed values in `propertyValues`, but that field is descriptive and
per-asset. It is not a global enumeration and must not be used to invent combinations.

**Phase 2 — Create the component.** `penpot.library.local.createComponent(shapes)` and set
`component.name`. Repeat build+create for every remaining variant of the asset.
✋ Checkpoint: all variants look correct.

Create each planned main component exactly once. Do not create temporary standalone components,
duplicate a variant under a second name, or create a second component as a fallback after an
unknown result. Every created main must already have one planned parent asset and one unique
variant tuple in the manifest.

**Phase 3 — Group into a variant container.** Use the high-level helper (handles the
multi-step workflow):

```js
const mains = penpot.currentPage.findAllShapes(sh => sh.isMainComponent() && /* this asset */);
const container = penpotUtils.createVariantContainer(mains.map(m => ({
  shape: m,
  properties: /* variant.properties, axes in plan order */
})));
```

For an existing group, `variantContainer.appendChild(mainInstance)` then
`setVariantProperty(pos, value)`. ✋ Checkpoint: swap UI works.

Run the final grouping exactly once per planned parent asset, after all and only the declared
variant mains exist. Select mains by the manifest's exact variant IDs/property tuples, never by
loose name matching. If grouping fails or leaves a main outside the container, stop and report
the incomplete run; do not create another container or retry the grouping mutation blindly.

**Phase 4 — Validate + report.** Confirm `tokenOverview()` resolves, no duplicate
  asset or variant identities, export the asset, and compare observed/classified/planned/created/local-or-
  unresolved/skipped counts. A complete observation set with a selective import is valid;
 do not mark it incomplete merely because every rendering did not become a library variant.
 Report the classification totals.

Do not one-shot the whole plan; go asset by asset, variant by variant, and validate
between.

## Existing assets and explicit modes

In additive mode, reconcile by `assetKey` and `variantKey` metadata before falling back to
display names. If an identity already exists, reuse it only when its structure and required
postconditions are compatible. If it differs, STOP and report a conflict.

- **Default on collision: STOP.** Halt the write, surface the planned identity versus the
  actual Penpot state, and do not proceed until told how to handle it.
 - **Permitted after the applicable human approval checkpoint in additive mode:** reuse compatible
   objects or create approved missing objects. These are not Auto-fix actions.
- **Design-system-change mode only:** updates, renames, rebinds, or structural changes require
  an explicit mode, affected identities, a reason, and an expected postcondition.
- Never silently duplicate.

## Critical rules

1. In additive mode, never modify, replace, extend, or re-bind an existing asset. Reconcile by
   stable identity before creating; on incompatibility, STOP and surface it.
2. Bind with `applyToken`; do not hardcode hex/px when a token exists in the plan.
3. Tokens must be active and resolvable (`resolvedValue` defined) or the binding is
   cosmetic only.
4. One main component per variant; group them with `createVariantContainer` (not the
   raw `createVariantFromComponents` unless you follow its exact multi-step order).
 5. Detach before mutating shared children of a component instance only inside an explicitly
    approved, identified design-system-change mutation. Never use `detach()` as an automatic
    recovery or additive-mode fallback; record the reason and expected postcondition.
6. Visually self-review each variant with `export_shape` (max 2 fix iterations, then
   present with defects named).
7. Verify any uncertain API with `penpot_api_info`.
8. Do not silently downsample an approved asset plan. Create every planned variant; if a variant
   cannot be created, stop or record it explicitly with its reason and evidence.
9. Reusable icon assets must remain separate components and parent icon slots must use real
   component instances.
10. Placement-axis values are evidence-derived per asset; never apply a hardcoded
    `IconPosition` enum. `IconPosition=None`, when present, omits the icon slot entirely.
11. Every mutation is exactly-once. Never issue the same mutation twice, and never retry an
    unknown mutation outcome without read/reconcile evidence.
12. A logical parent asset may have only one final VariantContainer. Orphan mains, duplicate
    containers, duplicate property tuples, and variants outside their declared group are failures.
13. In `design-system-change` mode, every existing-object mutation requires an explicit change
    reason, affected identity, and postcondition; never infer permission from a name collision.

## Report

End with: assets/variants created (net-new only), token bindings applied (and any
unresolved), any name collisions surfaced (STOPPED, pending human decision), and anything
still needing human review in Penpot's UI. Include the mutation manifest summary: planned,
executed once, reconciled, and blocked/unknown counts.
