# Design-Pipeline Manifest

- Version: 0.4
- Date: 04.09.2026
- Author: Georg Rinnhofer

## General

This manifest describes the overall human-defined goals, paradigms and parameters of the current project.

This is a human-authored source-requirements and management document. It defines the purpose, priorities and non-negotiable outcome expectations of DPIP; it is not a programming specification.

The operational interpretation is delegated to the project README, architecture and interpretation documents, skills, contracts, schemas and tests. These documents must remain traceable to the goals of this manifest. Technical or platform-specific constraints may add implementation rules, but they must be identified as such and may not weaken the requirements of this manifest.

## Document hierarchy

The direction of derivation is:

```text
Human Manifest → README / interpretation → Skills / contracts → Schemas / tests
```

The manifest is the human source of intent. The documents below it translate that intent into operational rules and evidence. Reports record experience and findings; they do not silently become new requirements. Human decisions are required whenever an operational interpretation materially changes the intent of this manifest.

## Versioning and change impact

The currently approved Manifest version is the explicit version stated in this document. Every
workflow run, derived technical document, contract, schema and test suite that depends on this
Manifest must record the exact Manifest version it implements or uses. A reference to "the latest"
version may be used for human navigation only; it must never be used as an execution dependency.

Existing runs remain governed by the Manifest version recorded when they started. They must not be
silently reinterpreted under a later version. New runs use the current approved version unless a
human explicitly authorizes another compatible version.

Changes are classified by their effect on human intent:

- **Patch:** typo fixes and wording clarifications that do not change the intended outcome. They
  require a documentation review and may be declared behaviour-neutral.
- **Minor:** additive goals, constraints or clarifications that expand the intended outcome without
  invalidating the existing one. They require an impact review of derived documents, contracts and
  tests before use.
- **Major:** changes that remove, weaken, redefine or materially alter an existing requirement.
  They require explicit human approval, migration or revalidation of affected workflows, and a
  new compatibility decision for existing artefacts.

If it is unclear whether a change affects behaviour, it must be treated as behaviour-affecting until
reviewed. The Manifest version and the impact decision must be preserved with the change record.

A patch-version change, such as `0.2` to `0.2.1`, does not invalidate references to `0.2` and does
not invalidate runs or artefacts that were correctly created under `0.2`. Those references remain
valid historical and provenance references. The patch version becomes the exact pin for new runs
only after the revised Manifest is approved. A prior exact version is not silently rewritten to the
new patch version, and it is not an acceptable substitute for the current exact pin on new work.

## Goals

A set of agents and skills should support the following workflow:

AI-supported workflow of the frontend design and implementation process with human control points (Quality Gates). The initial focus is on CCS, while reusability for other projects is a mandatory requirement.

The workflow should reduce manual labor while preserving human authority, design-system quality, traceability and the ability to reject uncertain or unsuitable results.

## Envisioned Process Flow

Source Material

Design input documents such as web content, PDFs, images, and other reference materials (e.g. Figma files). Sources are not assumed to be equivalent: the achievable automation level and quality depend on the source's structure, completeness and semantic information. A source that does not provide sufficient evidence must not be treated as a sufficient basis for fully automated reconstruction of complex components.

### Design System Building Blocks Creation

Automated and standardized generation of parts of the design system in Penpot. Building blocks are based on provided source documents and may be generated automatically, proposed for review, or left for manual creation depending on the evidence available.

### Quality Gate 1

Quality Gate 1 is a mandatory human decision point for the design-system building blocks. The detailed review criteria and evidence requirements are defined in the derived operational documents. A failed gate stops the affected flow until a human decision is recorded.

Benefit: reduction of manual labor; better quality due to a "no shortcut" policy; complete coverage of the approved scope instead of "I create what I need now" thinking.

### Design Generation

Automated creation of designs based on predefined rules and textual descriptions (PBIs) in the design system, utilizing the established design system building blocks.

### Quality Gate 2

Quality Gate 2 is a mandatory human decision point for the generated design. The detailed review criteria and evidence requirements are defined in the derived operational documents. A failed gate stops the affected flow until a human decision is recorded.

Benefit: reduction of manual labor; consistent frontend design; Penpot as visual control; direct configuration in Penpot possible instead of prompt trial and error.

### Frontend Component Code Generation

Automated generation of frontend component code while adhering to the defined design specifications and project-specific coding guidelines.

### Quality Gate 3

Quality Gate 3 is a mandatory human decision point for generated frontend component code. The detailed review criteria and evidence requirements are defined in the derived operational documents. A failed gate stops the affected flow until a human decision is recorded.

Benefit: reduction of manual labor; consistent code; increase of delivery speed.

## Paradigms

- Always use a three-layer token structure: primitives <- semantics <- components.
- Raw values may only be set at the primitives level.
- Semantics may only reference primitives.
- Components may only reference semantics.
- Governed visual properties of generated objects must use persisted bindings to the components layer; a merely equal direct value does not satisfy this principle.
- Logical objects (e.g. buttons and dropdowns) should be modeled as reusable assets with variants where variant modeling is appropriate. Only observed or explicitly approved variants may be created; unknown axes and unsupported combinations must not be invented.
- It is allowed to add, update and delete tokens in Penpot. Penpot is the main control tool; the import is a supporting process. Automated imports are additive by default, and changes to existing configuration require an explicitly approved change mode.
- Defensible estimates may be imported as review-required provisional values when the source provides a concrete basis for estimation, even when the evidence is incomplete or approximate. Such values must preserve their estimated value, confidence, source evidence, inference reason and machine-readable `requiresReview=true` status.
- A review-required value is usable for iterative workflow progress but is not considered governance-final until a human accepts or corrects it.
- The workflow may propose and provisionally include a token for an operationally useful component property even when the source does not provide sufficient evidence for its value, provided that the proposal is clearly identified for human review and is not treated as final.
- Review-required values must not be encoded through token-name suffixes such as `-guessed` or `-provisional`; uncertainty belongs in metadata and review reporting, not semantic identity.
- The workflow has to be reproducible for the same versioned input and approved starting state. A repeated run on an unchanged state must result in the same effective result or an explicit conflict. Uncertainty must be surfaced for human decision rather than silently hidden. A defensible estimate may be imported provisionally, provided its uncertainty is preserved as machine-readable review metadata; unsupported values must remain gaps unless a human approves a placeholder.
- It has to be possible to update an existing Penpot configuration without destroying it, e.g. by providing additional sources. Those additional sources may or may not contain information that is already available in the target system. The workflow must cope with this in a non-destructive, traceable manner and must not silently overwrite conflicting human decisions.

## Human control and accountability

Human reviewers retain authority over source suitability, design-system interpretation, uncertain or conflicting results, and changes to existing shared assets. The operational documents must make these decisions visible, traceable and reversible without turning this manifest into a technical procedure.

## Change record for version 0.4

- Classification: Minor
- Decision: Approved by the human principal on 04.09.2026.
- Intent: permit clearly identified workflow proposals for operationally useful token values when source evidence is insufficient, while preserving human review authority.
- Impact: derived operational documents, contracts, compiler behaviour and regression tests must identify Manifest `0.4` for new runs.
- Compatibility: existing runs and artefacts pinned to Manifest `0.3` or earlier remain governed by their recorded Manifest version and are not silently reinterpreted.

## Parameters

- design system: Penpot
- primary system environment for frontend development: A1 CCS
