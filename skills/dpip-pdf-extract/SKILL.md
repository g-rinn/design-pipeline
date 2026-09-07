---
name: dpip-pdf-extract
description: Use in the Design-Pipeline (dpip) workflow when a PDF source must be rendered into page images and text for downstream visual observations. Produces a manifest consumable by dpip-image-extract and dpip-design-tokens. Front-load keywords: dpip, design pipeline, pdf, render, pages, png, extract text, ocr.
---

# PDF Extract

Convert a PDF into per-page images and extracted text, stored in the project folder
so downstream skills (notably `dpip-image-extract` and `dpip-design-tokens`) can analyze both the visual
and the textual content.

## Manifest lineage

This skill is an operational derivative of the human requirements in
`C:\dev\direct-import\human-manifests\dpip-manifest.md` version `0.2`, interpreted through
`C:\dev\direct-import\dpip\README.md`.

PDF extraction supplies evidence for later human-controlled decisions; it must not imply that a
PDF provides the semantic information required for fully automated reconstruction of complex
components. Reports and extraction artefacts are evidence, not new requirements.

Record the exact Manifest version used for the extraction run. Do not use an unqualified "latest"
reference for execution; later Manifest versions require impact review for new downstream work.

## Objective (single)

Turn one PDF into: rendered page images (default PNG) + per-page text + a manifest
that links each text file to the image it came from.

## Inputs & constraints

- Input: exactly one PDF (local path).
- Default image format: **PNG**. Optional JPG via `--format jpg`.
- Default resolution: 150 dpi.
- Output lives **in the project folder** (the current workspace), under
  `.design-extraction/<pdf-stem>/`, so it is committed alongside the source for
  future reference.

## How to run

A ready-to-use script ships beside this skill: `pdf_extract.py` (same folder). It
renders and extracts text in a single pass per page using PyMuPDF.

```powershell
python "<this-skill-dir>\pdf_extract.py" "<path\to\input.pdf>"
```

Options: `-o <out-dir>`, `--dpi <n>` (default 150), `--format png|jpg` (default png).

Verify availability first; install if missing:

```powershell
python -c "import pymupdf" 2>$null; if ($?) { "ok" } else { python -m pip install pymupdf }
```

Fallbacks if Python/PyMuPDF is unavailable: `pdftoppm -png` + `pdftotext` (poppler),
or Ghostscript `gswin64c -sDEVICE=png16m`. Prefer PyMuPDF — it needs one dependency
for both images and text. 

## Output layout

```
.design-extraction/<pdf-stem>/
  images/0001.png      # page 1 .. N, zero-padded, format per --format
  text/0001.txt        # plain text of the same page (same zero-padded number)
  manifest.json        # authoritative link between each text file and its image
```

The page number is the shared key: `text/0001.txt` corresponds to `images/0001.png`.

## Manifest (the image reference)

`manifest.json` is the structured reference every downstream consumer should read. For
each page it records the relative image path, the relative text path, and metadata:

```json
{
  "schemaVersion": "1.0",
  "source": "C:/absolute/path/input.pdf",
  "pageCount": 12,
  "format": "png",
  "dpi": 150,
  "outputDir": "C:/absolute/path/.design-extraction/<stem>",
  "pages": [
    { "page": 1, "image": "images/0001.png", "text": "text/0001.txt", "charCount": 1234 }
  ]
}
```

`pages[].image` is the reference linking the extracted text back to the exact rendered
image it was parsed from. `schemaVersion` is the contract key (currently `1.0`); bump the
major on breaking shape changes, the minor on additive ones.

## Notes

- Do not OCR; extract embedded text via `page.get_text("text")`. If a page has no
  extractable text, `charCount` will be `0` and the text file will be empty — flag this
  as a gap for the consuming skill.
- Keep text files clean (no added headers); the manifest owns the linkage so text stays
  directly parseable downstream.

## Report

End with: output directory, page count, image format/dpi, and the path to
`manifest.json`. Point the user (or the next skill) at the manifest as the entry point.
