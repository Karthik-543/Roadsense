import json
import re
from pathlib import Path

INPUT = Path("data/processed")
OUTPUT = INPUT / "chunks"
OUTPUT.mkdir(exist_ok=True)
MANIFEST_PATH = Path("data/raw/source_manifest.json")
LOGS_PATH = Path("logs")
LOGS_PATH.mkdir(exist_ok=True)

# Chunking Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Load manifest lookup
manifest_by_stem = {}
if MANIFEST_PATH.exists():
    manifest_data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for item in manifest_data:
        stem = Path(item["local_path"]).stem
        manifest_by_stem[stem] = item

# Document category mapping based on path/topics
def infer_category(stem, topics, doc_type):
    stem_l = stem.lower()
    if "pothole" in stem_l:
        return "potholes"
    elif "distress" in stem_l or "terminology" in stem_l:
        return "pavement_distress"
    elif "safety" in stem_l:
        return "road_safety"
    elif "nsv" in stem_l or "roughness" in stem_l:
        return "pavement_condition"
    elif "env" in stem_l or "weather" in stem_l or "climate" in stem_l:
        return "weather_climate"
    elif "geotech" in stem_l or "drainage" in stem_l:
        return "drainage_subgrade"
    elif "traffic" in stem_l:
        return "traffic_maintenance"
    elif "research" in doc_type or "0926580521" in stem_l or "2209" in stem_l or stem_l == "main":
        return "research_detection"
    return "general_engineering"

total_chunks_count = 0
processed_docs_count = 0

for pages_json in INPUT.glob("*_pages.json"):
    data = json.loads(pages_json.read_text(encoding="utf-8"))
    stem = pages_json.stem.replace("_pages", "")
    manifest_info = manifest_by_stem.get(stem, {})

    source_id = data.get("source_id", stem)
    title = data.get("title", stem)
    org = data.get("organization", "Unknown")
    year = data.get("year", "Unknown")
    doc_type = data.get("document_type", "document")
    url = data.get("official_url", "")
    category = infer_category(stem, manifest_info.get("topics", []), doc_type)

    pages = data.get("pages", [])
    chunks = []

    # Reconstruct document with page markers & extract chunks cleanly
    current_text = ""
    page_map = [] # character index -> page number

    for p in pages:
        p_num = p["page"]
        p_text = p["text"]
        start_idx = len(current_text)
        current_text += p_text + "\n"
        end_idx = len(current_text)
        page_map.append((start_idx, end_idx, p_num))

    def get_page_range(char_start, char_end):
        start_p = 1
        end_p = 1
        for s_idx, e_idx, p_num in page_map:
            if char_start >= s_idx and char_start <= e_idx:
                start_p = p_num
            if char_end >= s_idx and char_end <= e_idx:
                end_p = p_num
        return start_p, max(start_p, end_p)

    start = 0
    chunk_idx = 0

    while start < len(current_text):
        end = min(start + CHUNK_SIZE, len(current_text))

        # Avoid splitting words abruptly if possible
        if end < len(current_text):
            next_space = current_text.find(" ", end)
            if next_space != -1 and next_space - end < 50:
                end = next_space

        chunk_str = current_text[start:end].strip()

        if len(chunk_str) > 30: # Ignore tiny noise chunks
            p_start, p_end = get_page_range(start, end)

            # Try extracting section header if first line looks like one
            lines = [l.strip() for l in chunk_str.split("\n") if l.strip()]
            section = lines[0][:80] if lines else "General"

            chunks.append({
                "chunk_id": f"{stem}_{chunk_idx}",
                "document": f"{stem}.txt",
                "source_id": source_id,
                "source_title": title,
                "organization": org,
                "year": year,
                "document_type": doc_type,
                "category": category,
                "page": p_start,
                "page_end": p_end,
                "section": section,
                "official_url": url,
                "provenance": f"{title} ({org}, {year}), p. {p_start}",
                "text": chunk_str
            })
            chunk_idx += 1

        if end == len(current_text):
            break

        start = end - CHUNK_OVERLAP

    output_file = OUTPUT / f"{stem}_chunks.json"
    output_file.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    total_chunks_count += len(chunks)
    processed_docs_count += 1
    print(f"{stem}.txt: {len(chunks)} chunks (Pages 1-{data.get('total_pages', '?')})")

# Save ingestion config log
ingestion_config = {
    "chunk_size": CHUNK_SIZE,
    "chunk_overlap": CHUNK_OVERLAP,
    "documents_processed": processed_docs_count,
    "total_chunks": total_chunks_count,
    "category_count": len(set(infer_category(p.stem.replace("_pages", ""), [], "") for p in INPUT.glob("*_pages.json")))
}

(LOGS_PATH / "ingestion_config.json").write_text(
    json.dumps(ingestion_config, indent=2),
    encoding="utf-8"
)

print(f"\nChunking completed: {total_chunks_count} chunks from {processed_docs_count} documents.")