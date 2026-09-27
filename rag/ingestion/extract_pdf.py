import pymupdf
import json
from pathlib import Path

PDF_PATH = Path("data/raw")
OUTPUT_PATH = Path("data/processed")
MANIFEST_PATH = Path("data/raw/source_manifest.json")

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# Load manifest for metadata lookup
manifest_by_stem = {}
if MANIFEST_PATH.exists():
    manifest_data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for item in manifest_data:
        stem = Path(item["local_path"]).stem
        manifest_by_stem[stem] = item

processed_files = []

for pdf_file in PDF_PATH.rglob("*.pdf"):
    doc = pymupdf.open(pdf_file)
    meta = manifest_by_stem.get(pdf_file.stem, {})

    pages_text = []
    full_text_with_markers = ""

    for i, page in enumerate(doc):
        page_num = i + 1
        txt = page.get_text()
        pages_text.append({
            "page": page_num,
            "text": txt
        })
        full_text_with_markers += f"\n[--- PAGE {page_num} ---]\n" + txt

    output_txt = OUTPUT_PATH / f"{pdf_file.stem}.txt"
    output_txt.write_text(full_text_with_markers, encoding="utf-8")

    output_pages = OUTPUT_PATH / f"{pdf_file.stem}_pages.json"
    output_pages.write_text(
        json.dumps({
            "source_id": meta.get("source_id", pdf_file.stem),
            "title": meta.get("title", pdf_file.stem),
            "organization": meta.get("organization", "Unknown"),
            "year": meta.get("year", "Unknown"),
            "document_type": meta.get("document_type", "document"),
            "official_url": meta.get("official_url", ""),
            "local_path": str(pdf_file.relative_to(PDF_PATH.parent.parent)),
            "total_pages": len(doc),
            "pages": pages_text
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    processed_files.append(pdf_file.name)
    print(f"Extracted: {pdf_file.name} ({len(doc)} pages) -> {output_txt.name}")

print(f"\nPDF extraction completed for {len(processed_files)} documents.")