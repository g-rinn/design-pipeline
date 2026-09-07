---
name: dpip-design-tokens
description: Use ALWAYS in the Design-Pipeline (dpip) workflow when creating, extracting, updating, renaming, or deleting design tokens. Consumes visual-observations documents from dpip-image-extract plus web, code/CSS, existing token files, or briefs. Maintains a W3C DTCG (2025.10) three-layer token system for Penpot. Front-load keywords: dpip, design pipeline, design tokens, token, tokens, dtcg, primitives, semantics, components, palette, color, spacing, radius, typography.
---

# Design Tokens

The authoritative skill for **any** design-token work. If a request touches tokens at
all — create, extract, update, rename, delete, or audit — use this skill. It owns a
single W3C DTCG (2025.10) 3-layer token spec and its usage manifest, and keeps them
consistent across every operation.

## Manifest lineage

This skill is an operational derivative of the human requirements in
`C:\dev\direct-import\human-manifests\dpip-manifest.md` version `0.2`, interpreted through
`C:\dev\direct-import\dpip\README.md` and constrained by
`C:\dev\direct-import\dpip\core-guardrails.md` and `contract.json`.

The manifest remains the source of human intent; this skill supplies executable token rules and
must not weaken its token-layer, human-control, reproducibility, source-suitability or
non-destructive-update expectations. Reports and historical artefacts are evidence only.

The exact Manifest version for this skill's run must be recorded in the run artefact and output
metadata. Do not resolve the governing requirements through an unqualified "latest" reference.
Existing artefacts remain tied to the Manifest version under which they were created; a changed
Manifest requires impact review before new output is generated.

Authoritative spec: <https://www.designtokens.org/tr/2025.10/> (format module:
<https://www.designtokens.org/tr/2025.10/format/>).

Pipeline position (text-only stage): visual sources are pre-processed upstream, never
read here.

```
PDF -> dpip-pdf-extract (PNG images) -> dpip-image-extract (observations doc) -> dpip-design-tokens -> dpip-penpot-tokens
```

## Restate the brief as a token-aware contract

Before acting, reframe the request:

- **Context** — the input(s) and their format(s).
- **Objective** — one operation: `create`/`extract`, `update`, `rename`, or `delete`.
- **Inputs** — files/URLs/existing spec, plus any explicit brand constraints.
- **Constraints** — the layer and naming rules below are non-negotiable.
- **Acceptance criteria** — quantitative: every reference resolves, zero raw values
  outside the primitives layer, zero name overlaps, all names dot-separated lowercase.

Act as a senior design-systems engineer. Record a justified reason for every change.

## Operation router

Determine the single operation and route:

| User intent | Operation | Section |
| ----------- | --------- | ------- |
| Build/extract a system from an input | `create` / `extract` | "Create / extract workflow" |
| Change a value, description, or binding | `update` | "Update workflow" |
| Rename a token or group | `rename` | "Rename workflow" |
| Remove a token or group | `delete` | "Delete workflow" |

If the request is only "convert this PDF", that is `dpip-pdf-extract`; only "analyze /
describe this image", that is `dpip-image-extract`. This skill operates on text/structured
inputs, never raw images or PDFs.

## Inputs (text only)

This skill does **not** read images or PDFs. Gather facts from textual/structured sources:

| Input | Read with | Provides |
| ----- | --------- | -------- |
| Visual-observations document | `read` (text) | `palette`, `typography`, `spacing`, `radius`, `elevation`, `opacity`, `layout`, `components`, `text` — from `dpip-image-extract` |
| Web content | `webfetch` | computed styles, CSS variables, layout tokens |
| Code / CSS / HTML / DESIGN.md | `read` (text) | explicit hex, px, font family/size, token names |
| Existing token file | `read` | current `tokens`/`layers`/`usage` to update in place |
| Manual brief | prompt | stated brand colors, scale, naming constraints |

If a raw image or PDF is handed to you, route it upstream first (`dpip-image-extract` /
`dpip-pdf-extract`) and read the resulting text document; do not inspect the pixels yourself.

**Combine multiple text sources.** Prefer explicit values (CSS hex, px, font family,
token names) over estimated ones; when sources disagree, prefer the explicit value,
record both, and note the conflict as an assumption.

Do not silently invent a value you cannot observe. Record a missing/unreadable value as
a **gap** (see "Report") instead of guessing.

## Deterministic extraction contract

For `create`/`extract`, this skill is a pure text transformation:

```text
observations.json + written token rules -> proposed token specification
```

It MUST NOT read historical token specs, asset plans, changelogs, Penpot state, or conversation
context. Existing token specs are inputs only for the explicit `update`, `rename`, and `delete`
operations. Penpot is checked later by `dpip-penpot-tokens`; it does not influence extraction.

Two runs over the same normalized observations and the same written rules MUST produce the same
canonical `tokens`, `layers`, `usage`, `gaps`, and `meta.confidence`. Audit-only fields such as
`processedAt` and `RUN_ID` are excluded from the fachliche hash.

The executable reference implementation is `C:\dev\direct-import\dpip\compile_tokens.py`.
For `create`/`extract`, use the compiler to produce the token tree; the agent may explain or
report the result but must not author an alternative token tree by free-form reasoning. The
compiler has no Penpot access and accepts only one observations document and one output path.

## Normalization rules

Process observation sections in this fixed order:

```text
palette -> typography -> spacing -> radius -> elevation -> opacity -> layout -> component usages
```

Before deriving tokens:

- normalize colors to uppercase HEX where HEX is available;
- normalize dimensions to one declared unit and preserve unsupported units as gaps;
- normalize font family, weight, and size spelling;
- preserve `observed`, `interpreted`, `unknown`, `approx`, evidence, and confidence separately;
- deduplicate exact normalized values only;
- never merge near-identical values without an explicit written tolerance rule;
- sort primitive facts, semantic roles, component usages, references, and gaps canonically;
- if two facts cannot be resolved by these rules, emit a gap instead of choosing by discretion.

Input order, object-key order, screenshot position, and model narration MUST NOT affect the
result.

## Fact classes and inclusion matrix

Classify every candidate fact exactly once before token derivation:

```text
component-visual | component-layout | component-typography | component-spacing |
component-state | documentation-only | measurement-only | unknown
```

Only `component-visual`, `component-typography`, `component-spacing`, and
`component-state` may directly produce tokens. `documentation-only`, `measurement-only`, and
`unknown` produce no token; they produce a gap only when the missing fact affects an approved
component decision.

Use this fixed inclusion matrix:

| Candidate | Emit primitive when | Otherwise |
| --- | --- | --- |
| Control fill, stroke, or text color | observed on a reusable control and typed | gap or exclude annotation |
| Control typography | observed or defensibly estimated on a reusable control and typed; estimates require review metadata | gap when no defensible basis exists |
| Control spacing | explicitly measured, repeated, or defensibly estimated from reusable controls; estimates require review metadata | gap when no defensible basis exists |
| Control radius | explicit, repeated, or defensibly estimated from reusable controls; estimates require review metadata | gap when no defensible basis exists |
| Opacity | explicitly documented or independently measurable | gap; do not infer from a lighter color |
| Dimension | numeric value is observed, defensibly estimated, or covered by an approved proposal basis; estimates and proposals require review metadata | preserve behaviour or gap |
| Layout behaviour | never as a raw primitive value | record for asset mapping |

Documentation headings, measurement guides, selection outlines, and explanatory copy are not
component facts unless the observations explicitly classify them as reusable control content.

## Canonical names and semantic derivation

Normalize state labels with this fixed table before naming tokens:

```text
"Hover & Focus" -> "hover-focus"
"Disabled Red"  -> "disabled-red"
"Disabled Grey" -> "disabled-grey"
```

Other values explicitly classified by the observations as states are normalized mechanically:
Unicode-normalize, trim, lowercase, replace each run of non-alphanumeric characters with one
hyphen, and remove leading/trailing hyphens. No translation or semantic synonym is allowed.
Visible text such as `"Bitte warten..."` remains content unless the observations explicitly
classify it as a state.

Derive semantic roles from the fixed tuple:

```text
component family + visual role + normalized state
```

For example:

```text
Button + fill + Primary + Default -> color.action.primary.default
Button + fill + Primary + HoverFocus -> color.action.primary.hover
Button + border + Secondary + Default -> color.action.secondary.default.border
```

Each semantic token references exactly one primitive. If one role maps to conflicting primitive
values, do not choose or merge them: emit a conflict/gap or derive separate roles only when the
source evidence proves that the roles differ.

Emit a component token only when an observed usage identifies the component, property, and
semantic role. A component token may be reused by multiple variants; usage is recorded once per
component token. The existence of a state or axis alone is not sufficient reason to create a
token.

## Gap identity

Every gap has a stable identity:

```text
domain + reasonCode + token
```

Free-text explanations may describe the gap but do not determine its identity. Use explicit
reason codes such as `fixed-size-not-proven`, `unmeasurable-disabled-opacity`,
`unknown-icon-geometry`, or `unresolved-semantic-role`. Deduplicate equal gap identities before
writing the output.

## Closed token decision matrix

The following matrix is exhaustive. For every candidate fact, evaluate rows from top to bottom
and return exactly one result: `exclude`, `gap`, or `emit`.

| Priority | Condition | Result |
| --- | --- | --- |
| 1 | class is `documentation-only` or `measurement-only` and no approved control usage exists | `exclude` |
| 2 | class is `unknown`, required type is missing, or role is ambiguous | `gap` |
| 3 | class is eligible but no concrete component/property usage exists | `exclude` |
| 4 | color is a typed control fill, stroke, text, or icon color | `emit primitive` |
| 5 | typography is a typed reusable control text style | `emit primitive` |
| 6 | spacing is explicitly measured or occurs on at least two reusable controls | `emit primitive` |
| 7 | radius is explicit or occurs on at least two reusable controls | `emit primitive` |
| 8 | opacity is explicitly documented or independently measurable | `emit primitive` |
| 9 | dimension behavior is `fixed` and the value is tokenizable | `emit primitive` |
| 10 | an approved proposal basis supplies a useful missing dimension value | `emit proposed primitive` |
| 11 | dimension behavior is `content-dependent` or `fill-available` | `record behavior; no primitive` |
| 12 | no earlier row applies | `gap` with `unclassified-token-candidate` |

No discretionary "nice to have" token is allowed. The first matching row wins. The same fact
cannot be both emitted and excluded.

## Closed token path templates

Use these exact templates; do not invent alternative names during a run. The tier name is not
repeated in the path because the layer already supplies that namespace.

```text
slug(value) = Unicode NFC -> trim -> lowercase -> replace every non-alphanumeric run with '-'

primitive color      = <family>.<uppercase-hex-without-hash-lowercased>
primitive dimension  = dimension.raw.<normalized-number-and-unit>
primitive spacing    = spacing.raw.<normalized-number-and-unit>
primitive radius     = radius.raw.<normalized-number-and-unit>
primitive fontFamily = font.family.<slug(normalized-family)>
primitive fontSize   = font.size.<normalized-number-and-unit>
primitive fontWeight = font.weight.<slug(normalized-weight)>
primitive opacity    = opacity.raw.<normalized-number>

semantic color fill   = color.action.<slug(family)>.<state-or-default>
semantic color stroke = color.border.<slug(family)>.<state-or-default>
semantic color text   = color.content.<slug(family)>.<state-or-default>
semantic color icon   = color.icon.<slug(family)>.<state-or-default>
semantic spacing      = spacing.<slug(component)>.<slug(property)>
semantic typography   = typography.<slug(component)>.<slug(property)>
semantic radius       = radius.<slug(component)>.<slug(property)>
semantic opacity      = opacity.<slug(component)>.<state-or-default>

component = <slug(component)>.<canonical-variant-path>.<slug(property)>
canonical-variant-path = sorted(slug(axis) + '-' + slug(value), axis ascending).join('.')
```

`state-or-default` is `default` when no explicit state exists. Optional values are omitted; no
placeholder value may be invented. Source names do not override these templates. Identical keys
with differing values are a hard conflict, not a merge opportunity.

### Technical Penpot compatibility rule: reserved `value` path segment

The literal path segment `value` MUST NOT be emitted in token or group names destined for Penpot.
This is not derived from the human Manifest and is not a semantic naming preference. It is a
reverse-engineered Penpot compatibility constraint: the Penpot GUI token-tree validator treats
`value` as a reserved structural name even though the Penpot API accepts such paths. Therefore the
compiler and import workflow use `raw` or deterministic family grouping instead. This technical
rule may be retained or corrected independently of human Manifest intent, but any correction must
be recorded as a technical compatibility decision.

## Closed gap rules

Every gap MUST have exactly these fields:

```json
{
  "key": "domain:reasonCode:token-or-empty",
  "domain": "dimension",
  "reasonCode": "fixed-size-not-proven",
  "token": "button.height",
  "affectsFinalToken": true,
  "reason": "fixed behaviour is observed but no numeric value is available"
}
```

Use exactly one of these reason codes when the corresponding condition occurs:

```text
missing-type
ambiguous-role
fixed-size-not-proven
unmeasurable-disabled-opacity
unknown-icon-geometry
unresolved-semantic-role
unclassified-token-candidate
unsupported-unit
conflicting-normalized-value
```

`reason` is selected from the fixed reason template for the code; it is not free-form model
narration. `affectsFinalToken` is true only when the missing fact blocks an otherwise eligible
token. Sort and deduplicate gap keys before output.

Reason templates are fixed:

```text
missing-type                  = "the candidate has no supported type"
ambiguous-role                = "the source role cannot be resolved uniquely"
fixed-size-not-proven         = "fixed behaviour is observed but no numeric value is available"
unmeasurable-disabled-opacity = "disabled opacity cannot be measured independently"
unknown-icon-geometry         = "icon geometry is visible but unavailable as a source asset"
unresolved-semantic-role      = "no unique semantic role can be derived"
unclassified-token-candidate  = "no closed inclusion rule applies"
unsupported-unit              = "the source unit is not supported for token conversion"
conflicting-normalized-value  = "identical normalized keys have conflicting values"

## Token inclusion and derivation rules

### Primitives

A primitive is emitted when the value is observed, defensibly estimated, or covered by an approved
proposal basis, has a known type, and survives exact normalization/deduplication. Approximate
values remain marked `inferred`; values supplied by an operational proposal remain marked
`proposed`. Both carry review metadata and set `requiresReview: true`. An unreadable or ambiguous
value with neither defensible evidence nor an approved proposal basis becomes a gap.

### Semantics

Derive semantic tokens from the fixed tuple `source role + component family + state` using the
existing naming conventions. A semantic token references exactly one primitive. If no unique
primitive satisfies the role, emit a gap and no semantic token.

### Components

Emit a component token only when a concrete observed usage identifies the component, property,
and semantic role. A token may be reused by multiple variants; usage is recorded once per
component token. Do not create a component token merely because a state or axis exists.

### Layout and sizing

Record layout behaviour separately from dimensions:

- `layout.axis`: `horizontal`, `vertical`, or `unknown`;
- dimension behaviour: `fixed`, `content-dependent`, `fill-available`, or `unknown`.

Only confirmed `fixed` behaviour may produce an evidence-derived fixed dimension token. When a
declared proposal basis supplies a useful missing dimension value, the compiler may emit a
`proposed` fixed dimension token instead. Dynamic behaviour remains a behavioural fact for the
asset stage. `unknown` produces a gap unless such a proposal basis applies.

## Confidence calculation

Confidence is mechanical and conservative:

```text
meta.confidence = minimum confidence of all emitted token decisions
```

Do not round upward, apply discretionary weights, or compensate for gaps. If no token decision
exists, use the observation-document confidence. The boundary is inclusive:

```text
meta.confidence >= 0.80 -> confidence gate passes
meta.confidence <  0.80 -> confidence gate fails
```

Set `requiresHumanReview` to true exactly when `meta.confidence < 0.80` OR at least one gap has
`affectsFinalToken: true` OR any emitted token has status `inferred`, `proposed` or `placeholder`.
Otherwise set it to false. Do not infer review status from prose.

## Canonical output rules

Every `create`/`extract` output MUST have this root shape, with these fields at document level:

```text
meta, tokens, layers, usage, gaps
```

`layers` MUST contain exactly `primitives`, `semantics`, and `components`. `usage` and `gaps`
MUST NOT be nested under `tokens`. Sort all arrays and object keys canonically before validation.
The fachliche comparison excludes only audit metadata explicitly marked as audit-only.

## The 3-layer model

There MUST be exactly three layers. References point strictly upward, never sideways
or down.

```
components   (usage)     -> references semantics ONLY, carries usage $description
    ^
semantics    (intent)    -> references primitives ONLY
    ^
primitives   (raw scale) -> raw values ONLY, never references
```

## Mandatory Penpot token-set convention

Every Penpot token import MUST create exactly these three sets, using the source/product
namespace as the customer identifier:

```text
[customer-identifier]/primitives
[customer-identifier]/semantics
[customer-identifier]/components
```

Workflow names and asset/source names MUST NOT appear in the set path. For example, the
`A1 Design` source uses `A1 Design/primitives`, `A1 Design/semantics`, and
`A1 Design/components` — never `dpip/...` or `.../Buttons/...`.

### Layer rules (hard constraints)

1. **Primitives** hold raw, context-free values only: hex colors, pixel/rem sizes,
   radii, font families/sizes/weights, line heights, letter spacing, shadow values,
   opacities. A primitive MUST NOT contain a `{ref}`.
2. **Semantics** express meaning/function. A semantic token's `$value` MUST be a
   `{ref}` to a primitive, and nothing else.
3. **Components** (the usage layer) express where a value is applied, e.g.
   `button.primary.bg`. A component token's `$value` MUST be a `{ref}` to a semantic
   token, and nothing else. Every component token MUST carry a `$description` stating
   where it is used (component, property, states).

## DTCG encoding rules (2025.10)

- An object with a `$value` property is a **token**; an object without `$value` is a
  **group**. `$type` is required on every token unless inherited from a parent group.
- References use curly-brace syntax: `"{color.action.primary.bg}"`.
- `$description` is a plain string documenting purpose (and, for the component layer,
  usage location). `$extensions` is available for vendor data. `$deprecated` marks a
  token as deprecated (true, false, or a string explanation).
- **Dot-separated names are NOT literal names.** The spec forbids `.`, `{`, and `}`
  in a token/group name. A dot-separated logical name maps to **nested groups**:
  `button.primary.bg` = group `button` -> group `primary` -> token `bg`.
- **No overlap** (the spec's "an object cannot be both a token and a group" rule):
  `button.primary` (a token) and `button.primary.something` (which needs `primary`
  to be a group) cannot coexist. Choose names so no token name is a prefix of another.

Canonical example of the mapping:

```json
{
  "color": {
    "$type": "color",
    "blue": {
      "500": { "$type": "color", "$value": { "colorSpace": "srgb", "components": [0.2, 0.4, 0.8], "hex": "#3366CC" } }
    },
    "action": {
      "primary": {
        "bg": { "$type": "color", "$value": "{color.blue.500}" }
      }
    }
  },
  "button": {
    "primary": {
      "bg": {
        "$type": "color",
        "$description": "Background of the primary button in its default state.",
        "$value": "{color.action.primary.bg}"
      }
    }
  }
}
```

Here `color.blue.500` is a primitive, `color.action.primary.bg` is a semantic, and
`button.primary.bg` is a component token.

## Naming rules

- Lowercase, dot-separated, no leading `$`.
- Globally unique across all three layers.
- No prefix overlap (no `button.primary` alongside `button.primary.something`).
- Use well-known abbreviations only (`btn` for button, `bg`/`fg`, `md`/`sm`/`lg`,
  `nav`, `info`, `h1`..`h6`, `spacing` -> `sp` is NOT well-known). Otherwise prefer
  full, readable strings.
- Common prefixes per tier: primitives use scale-style names (`blue.500`, `spacing.16`,
  `radius.md`, `font.size.300`); semantics use intent (`color.text.default`,
  `color.action.primary.bg`, `spacing.inset.md`); components use component + property
  (`button.primary.bg`, `input.border.default`).

## Canonical output format (spec file)

The JSON document is the canonical proposed token specification for a run. Penpot remains the
source of truth for existing token sets, tokens, bindings, and active values; this document is
evidence, a reviewable delta, and an audit input, not an automatic overwrite target:

```json
{
  "meta": {
    "schemaVersion": "1.0",
    "spec": "https://www.designtokens.org/tr/2025.10/",
    "sources": [
      { "type": "observations | web | code | existing | brief", "uri": "...", "role": "hero | reference | spec" }
    ],
    "processedAt": "ISO-8601 timestamp",
    "confidence": 0.0..1.0
  },
  "tokens": {
    "...": "DTCG token tree: nested groups, each token = { $type, $value, [$description], [$deprecated], [$extensions] }"
  },
  "layers": {
    "primitives": ["color.blue.500", "spacing.16", "..."],
    "semantics": ["color.action.primary.bg", "..."],
    "components": ["button.primary.bg", "..."]
  },
  "usage": {
    "button.primary.bg": {
      "component": "Button",
      "property": "background",
      "states": ["default"],
      "variants": { "Hierarchy": ["Primary"] },
      "theme": "all | light | dark"
    }
  },
  "gaps": [
    { "domain": "responsive | motion | elevation | accessibility | internationalization | value",
      "token": "optional token path",
      "reason": "what is missing or unreadable" }
  ]
}
```

Field contracts:

- `tokens` is the canonical DTCG file (equivalent to a `.tokens.json`).
- `layers.<tier>` is a flat, deduplicated list of dot-separated token paths for that
  tier (fast validation and lookup).
- `usage` is the post-processing manifest: one entry per **component**-layer token,
  recording where it should be applied (`component` PascalCase, `property`, `states`,
  `variants`, `theme`). Follow-up agents use this to bind tokens to shapes.
- `meta.confidence` reflects how reliably the source could be read.

`create`/`extract` emits this document. `update`/`rename`/`delete` edit the **existing**
spec file in place — never regenerate and discard user data (see data-safety rules).

**Contract versioning:** `meta.schemaVersion` (currently `1.0`) is what downstream
consumers key off. Bump the major on breaking shape changes, the minor on additive ones.
Never change a field's meaning without bumping.

## Create / extract workflow

### Phase 1 — Normalize facts

1. **Prepare sources** — this skill consumes text only. If handed a PDF, route it to
   `dpip-pdf-extract`; if an image, to `dpip-image-extract`; then read the resulting document(s).
   Read observations and explicitly permitted source text only. Note anything missing as a gap.
2. **Normalize** — process sections in the fixed order and apply the normalization rules above.
   Deduplicate exact normalized values only; near-identical values remain distinct unless a
   written tolerance rule exists.

### Phase 2 — Derive and validate

3. **Extract primitives** — collect every eligible raw value (colors, spacing, radii, type,
   shadows, opacities) from the normalized facts.
4. **Derive semantics** — apply the fixed role/family/state rule; assign a `{ref}` to a primitive.
   Never use a raw value.
5. **Build components** — for each observed usage (button bg, input border, card
   padding, …), create a component token whose `$value` refs a semantic and whose
   `$description` + `usage` entry record where it is used.
   Include state-specific and variant-specific usages whenever visible in the
   observations; do not reduce a complete observation matrix to default-only tokens.
6. **Write manifests** — populate root-level `layers.*`, `usage`, and `gaps`.
7. **Canonicalize** — sort the output and calculate the fachliche comparison hash excluding
   audit-only metadata.
8. **Validate** — run the checklist below before returning.
9. **Confidence gate** — if the source observations document has `meta.confidence` below
   0.8, or an emitted token is approximate/inferred, mark the affected token and output as
   requiring human review. Do not discard a defensible estimate merely because it needs
   correction; it must not be presented as governance-final until reviewed. Values without a
   defensible basis remain gaps.

## Update workflow

1. **Locate** the token by its dot-separated path in `tokens`, `layers.*`, and (if a
   component) `usage.*`.
2. **Validate the new value** against the layer rules: raw value only for primitives;
   a `{ref}` to a primitive for semantics; a `{ref}` to a semantic for components.
   Enforce naming rules (unique, no prefix overlap).
3. **Apply** the change in `tokens`. If a primitive's raw value changes, note the
   semantics/components that inherit it (they resolve automatically — list them in the
   report).
4. **Sync** `layers.*` and `usage.*` if the change affects a name, type, or usage
   description (e.g. update `$description` and the matching `usage` entry together).
5. **Validate** the checklist.

## Rename workflow

A token name change is a structural edit because references use `{path}`.

1. **Find all references** to the old path (`{old.path}`) across the entire `tokens`
   tree — a rename must update every one of them, or the spec breaks.
2. **Check naming rules** for the new path: unique, dot-separated lowercase, and no
   prefix overlap with any existing token.
3. **Rename** the group/token key and rewrite every `{ref}` that pointed at it.
4. **Sync** `layers.*` (move the path) and `usage.*` (rename the key).
5. **Validate** the checklist, with special attention to no-orphan references.

## Delete workflow

Deletion is destructive — apply the data-safety rules first.

1. **Find references** to the token. If any `{ref}` points at it, deleting would orphan
   them. Prefer `$deprecated: true` (or a string reason) over hard deletion when the
   token may still be referenced.
2. **Confirm** with the user before a hard delete, listing what will be removed and
   any downstream references that will be resolved.
3. **Resolve or remove** every referencing token (repoint or delete) so no orphan
   remains.
4. **Remove** the token from `tokens`, `layers.*`, and `usage.*` (if a component).
5. **Validate** the checklist.

## Validation checklist (acceptance gates)

- [ ] Exactly three layers present; none empty without justification.
- [ ] Every semantic `$value` is a `{ref}` that resolves to a primitive.
- [ ] Every component `$value` is a `{ref}` that resolves to a semantic.
- [ ] No raw value appears outside the primitives layer.
- [ ] No token name is a prefix of another (no overlap).
- [ ] All names are lowercase, dot-separated, and unique.
- [ ] Every component token has a `$description` and a `usage` entry.
- [ ] `layers.*` lists match the `tokens` tree exactly (no orphan or missing path).
- [ ] (rename/delete only) No `{ref}` points to a missing token after the operation.
- [ ] (create/extract only) Confidence gate passed: `meta.confidence` >= 0.8, or the
      result is explicitly marked as needing human review.
- [ ] Every observed variant/state requiring a distinct visual token is represented in
      `usage` or listed as an explicit gap; no silent sampling.
- [ ] Root output shape is canonical: `meta`, `tokens`, `layers`, `usage`, `gaps`.
- [ ] `layers`, `usage`, and `gaps` are at document root; no duplicate or nested manifests.
- [ ] Two runs over the same normalized observations produce the same fachliche hash.

## Report

End with a structured summary: operation performed, tokens per layer, what changed and
why, affected downstream references, `meta.confidence`, any gaps, assumptions that need human
review, and the canonical fachliche hash. If you capped scope (top-N colors, sampled pages,
skipped a source, or used an unsupported value), say so explicitly.
