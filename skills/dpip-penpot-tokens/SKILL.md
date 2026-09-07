---
name: dpip-penpot-tokens
description: Use in the Design-Pipeline (dpip) workflow when a DTCG spec must be imported into Penpot as the exact customer/primitives, customer/semantics, and customer/components token sets. Validates upward references and never adds workflow or source names to the set path. Front-load keywords: dpip, design pipeline, penpot tokens, import tokens, token sets, primitives, semantics, components, dtcg.
---

# Penpot Tokens (import)

Import a `dpip-design-tokens` spec into Penpot as token sets + tokens, via the Penpot MCP.

Pipeline position (the write stage):

```
PDF -> dpip-pdf-extract -> dpip-image-extract -> dpip-design-tokens -> dpip-penpot-tokens (Penpot)
```

This is the token write stage; `dpip-penpot-assets` is the separate component write stage.
Universal mutation rules live in `C:\dev\direct-import\dpip\core-guardrails.md`.

## Preconditions

- The Penpot project must be connected to the MCP server (Penpot MCP Plugin).
- Call `high_level_overview` once before any Penpot action, then read tokens with
  `penpotUtils.tokenOverview()`.
- Input: the `dpip-design-tokens` spec file (JSON with `tokens`, `layers`, `usage`).
- All writes go through `execute_code`; `penpot.library.local.tokens` is the token
  catalog (`addSet`, `set.addToken`, `set.toggleActive`).

## Restate the brief

- **Context** — the spec file + the connected Penpot file's current token state.
- **Objective** — one goal: reconcile the approved token proposal with Penpot without
  overwriting existing values in additive mode, and ensure every approved reference resolves.
- **Inputs** — the spec's `tokens` tree and `layers.*` lists.
- **Constraints** — additive by default; no silent value or binding changes; references must
  resolve; values are strings.
- **Acceptance criteria** — `tokenOverview()` shows exactly the three customer-scoped sets;
  no unresolved refs; all conflicts are surfaced before mutation.

## Type mapping (DTCG -> Penpot)

Derive the Penpot token `type` from the spec token's `$type` plus its name prefix:

| Spec `$type` | Name prefix | Penpot `type` |
| ------------ | ----------- | ------------- |
| `color` | `color.*` | `color` |
| `dimension` | `spacing.*` | `spacing` |
| `dimension` | `radius.*` | `borderRadius` |
| `dimension` | `font.size.*` | `fontSizes` |
| `dimension` | (other) | `dimension` |
| `fontFamily` | `font.family.*` | `fontFamilies` |
| `fontWeight` | `font.weight.*` | `fontWeights` |
| `number` | `opacity.*` | `opacity` |
| `shadow` | `shadow.*` | `shadow` |
| `typography` | `font.*` / `text.*` | `typography` |

Reference tokens (semantics/components) keep the same `type` as the primitive they
reference — the spec already carries their `$type`, so the same table applies.

## Value conversion (DTCG -> Penpot string)

Penpot `addToken` `value` is **always a string** — a literal or a `"{reference}"`.

- **Reference** — if `$value` is a string starting with `{`, pass it through unchanged
  (e.g. `"{color.blue.500}"`).
- **Literal `color`** — if `$value` is an object, use `$value.hex`; if already a hex
  string, use as-is.
- **Literal dimension/spacing/radius/fontSize/fontWeight/opacity** — a number (or
  `{ value, unit }`) becomes its numeric string: `String(value)`. Penpot dimensions are
  px-based; flag `rem`/`%` for review rather than silently mis-scaling.
- **Literal `fontFamily`** — the family string.
- **Literal `shadow`** — pass the CSS-like `value` string if present; otherwise best
  effort (see below).
- **`typography` (composite)** — Penpot typography tokens are composite; inspect
  `penpot_api_info('TokenTypography')` first. If the spec only has `font.*` primitives,
  skip composite typography tokens and report them as a follow-up.

## Token descriptions

After creating a token, copy the spec's `$description` into Penpot's writable
`token.description` property when it is present. At minimum, every `proposed` token must receive
a concise human-readable description stating that it is proposed and why; keep the full confidence,
evidence, and proposal metadata in `$extensions.dpip`. Reused compatible tokens may have their
descriptions updated only when the import explicitly owns that metadata; never overwrite unrelated
existing descriptions.

When uncertain about a token type's value format, call `penpot_api_info('<TokenType>')`
before writing — guessing is the #1 cause of silent failures.

## Customer namespace resolution

The customer namespace is configuration and metadata, never an importer constant. Resolve it
before creating any sets, using this precedence:

1. An explicit `importConfig.customerNamespace` supplied by the governed workflow.
2. `spec.meta.customerNamespace`.
3. `spec.meta.customer`.
4. `spec.meta.project`.
5. A meaningful parent directory from `spec.meta.source.file` only when that metadata is
   explicitly marked as a project/source namespace.

If none is available, stop and request a namespace; do not silently invent one. The current
governed workflow supplies `A1 Design` through its external import configuration, so existing
imports retain the `A1 Design/*` grouping without hardcoding that value in this skill.

```js
const cleanNamespace = (value) => {
  const text = String(value ?? "").trim().replace(/[\\/]+/g, " ").replace(/\s+/g, " ");
  if (!text || text === "." || text === "..") return "";
  return text;
};

const resolveCustomerNamespace = (spec, importConfig = {}) => {
  const meta = spec?.meta ?? {};
  const source = meta.source ?? {};
  const explicit = cleanNamespace(importConfig.customerNamespace);
  const metadata = [
    meta.customerNamespace,
    meta.customer,
    meta.project,
    source.project,
    source.customerNamespace,
  ].map(cleanNamespace).find(Boolean);
  const customer = explicit || metadata;
  if (!customer) {
    throw new Error("missing customer namespace: set importConfig.customerNamespace or spec.meta.project");
  }
  return customer;
};
```

The importer may offer a deliberate `omitCustomerNamespace` option only outside the governed
workflow. It must not be enabled for a governed DPIP import, because the three customer-scoped
sets are part of the collision-avoidance contract.

## Set layout

Create exactly these customer-scoped sets, idempotently, and **activate** each (new sets are
inactive):

- `[customer]/primitives` <- `layers.primitives` (literal values)
- `[customer]/semantics` <- `layers.semantics` (references to primitives)
- `[customer]/components` <- `layers.components` (references to semantics; the set still exists if empty)

The referenced set must be **active** before adding a reference token, or validation
fails. Theming (splitting colour semantics into `modes/light` + `modes/dark`) is a future
extension — do it only if the spec carries per-theme colour values.

## Workflow

**Phase 0 — Discover.** `high_level_overview`; read the spec file; `tokenOverview()` to
see existing sets/tokens. Determine the explicit mode (`additive` or
`design-system-change`). In additive mode, any existing token with a differing type, value,
reference, or set is a conflict. ✋ Checkpoint: confirm the mode and proposed delta.

**Phase 1 — Primitives.** Create + activate `[customer]/primitives`, add each
`layers.primitives` token with a literal value. ✋ Checkpoint: review the primitive list.

**Phase 2 — Semantics.** Create + activate `[customer]/semantics`; add each `layers.semantics` token
with its `{ref}` value (primitives must be active). ✋ Checkpoint: review mappings.

**Phase 3 — Components.** Create + activate `[customer]/components`; add each
`layers.components` token with its `{ref}` value (semantic must be active).
✋ Checkpoint: review mappings.

**Phase 4 — Validate.** `tokenOverview()`; confirm each token's `resolvedValue` is defined
(no unresolved refs), no duplicate names, all three sets present. Report.

Do **not** one-shot the whole import; go tier by tier and validate between.

## Idempotency + helper snippet

```js
const tok = penpot.library.local.tokens;
const ensureSet = (name) => {
  const existing = tok.sets.find(s => s.name === name);
  if (existing) {
    if (!existing.active) throw new Error(`inactive existing set requires review: ${name}`);
    return existing;
  }
  const created = tok.addSet({ name });
  created.toggleActive();                    // new sets are INACTIVE
  return created;
};
const addIfCompatible = (set, type, name, value, description = "") => {
  const existing = set.tokens.find(t => t.name === name);
  if (!existing) {
  const created = set.addToken({ type, name, value });    // value is ALWAYS a string
    if (description) created.description = description;
  return { action: "create", name };
  }
  if (existing.type !== type || existing.value !== value) {
    throw new Error(`token conflict: ${set.name}/${name}`);
  }
  return { action: "reuse", name };
};

// primitives — importConfig is supplied by the workflow, not defined as an importer constant
const customer = resolveCustomerNamespace(spec, importConfig);
const prim = ensureSet(`${customer}/primitives`);
addIfCompatible(prim, "color", "color.blue.500", "#3366CC", "Observed brand blue.");
addIfCompatible(prim, "spacing", "spacing.16", "16", "Observed spacing value.");
// semantics (primitives must be active)
const sem = ensureSet(`${customer}/semantics`);
addIfCompatible(sem, "color", "color.action.primary.bg", "{color.blue.500}", "Semantic primary action background.");
return penpotUtils.tokenOverview();
```

## Critical rules

1. In additive mode, reconcile by set + token identity and exact type/value/reference; never
   silently accept an incompatible existing token.
2. Value is a string — literal or `"{reference}"`; numeric values are invalid.
3. New sets are inactive — `toggleActive()` every set you create.
4. References fail unless the referenced set is active — activate `[customer]/primitives`
   before adding semantics, `[customer]/semantics` before adding components.
5. Verify each tier with `tokenOverview()` (and `token.resolvedValue`) before moving on.
6. Verify any uncertain API with `penpot_api_info`.
7. In `design-system-change` mode, every existing-token change requires an explicit reason,
   affected set/token identity, and expected postcondition.

## Report

End with: sets created/reused (and explicitly approved updates, if change mode), token counts per set, any unresolved references, any
composite/typography tokens deferred, and whether the user still needs to toggle
theme/mode sets in Penpot's Tokens panel.
