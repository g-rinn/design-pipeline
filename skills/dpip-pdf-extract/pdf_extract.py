"""Convert a PDF to per-page images + extracted text, with a linking manifest.

Requires PyMuPDF (>= 1.23):  pip install pymupdf
Render + text extraction are done in one pass per page.

Usage:
  python pdf_extract.py <input.pdf> [-o OUT_DIR] [--dpi 150] [--format png]

Output layout (default OUT_DIR = <project>/.design-extraction/<pdf-stem>/):
  images/0001.png ...      rendered pages (format is png by default)
  text/0001.txt   ...      extracted plain text, one file per page
  manifest.json            links each page's text to its image + metadata
"""

import argparse
import json
import sys
from pathlib import Path


def _load_mupdf():
    try:
        import pymupdf as mupdf
    except ImportError:
        import fitz as mupdf  # older PyMuPDF import name
    return mupdf


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", help="path to the input PDF")
    ap.add_argument("-o", "--out", default=None, help="output directory (default: <project>/.design-extraction/<pdf-stem>)")
    ap.add_argument("--dpi", type=int, default=150, help="render resolution (default 150)")
    ap.add_argument("--format", default="png", choices=["png", "jpg"], help="image format (default png)")
    args = ap.parse_args(argv)

    mupdf = _load_mupdf()

    src = Path(args.pdf).resolve()
    if not src.exists():
        sys.exit(f"PDF not found: {src}")

    out = Path(args.out).resolve() if args.out else (Path.cwd() / ".design-extraction" / src.stem)
    img_dir = out / "images"
    txt_dir = out / "text"
    img_dir.mkdir(parents=True, exist_ok=True)
    txt_dir.mkdir(parents=True, exist_ok=True)

    doc = mupdf.open(src)
    n = len(doc)
    width = len(str(n))
    pages = []

    for i, page in enumerate(doc, start=1):
        num = f"{i:0{width}d}"
        img_rel = f"images/{num}.{args.format}"
        txt_rel = f"text/{num}.txt"

        pix = page.get_pixmap(dpi=args.dpi)
        pix.save(out / img_rel)

        text = page.get_text("text").strip()
        (out / txt_rel).write_text(text, encoding="utf-8")

        pages.append({
            "page": i,
            "image": img_rel,
            "text": txt_rel,
            "charCount": len(text),
        })

    manifest = {
        "schemaVersion": "1.0",
        "source": str(src),
        "pageCount": n,
        "format": args.format,
        "dpi": args.dpi,
        "outputDir": str(out),
        "pages": pages,
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(json.dumps({
        "manifest": str(out / "manifest.json"),
        "pageCount": n,
        "images": str(img_dir),
        "text": str(txt_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
