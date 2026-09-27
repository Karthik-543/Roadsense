from pathlib import Path
import os
import shutil

RAW = Path(r"D:\projects\Roadsense\data\raw\rdd2022")
BASE = Path(r"D:\projects\Roadsense\data\processed\rfdetr_rdd2022")

SPLITS = {
    "train": "train",
    "val": "valid",
    "test": "test",
}

for raw_split, out_split in SPLITS.items():
    src = RAW / raw_split / "images"
    dst = BASE / out_split / "images"
    dst.mkdir(parents=True, exist_ok=True)

    files = [
        p for p in src.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    ]

    linked = 0
    existing = 0

    for src_file in files:
        dst_file = dst / src_file.name

        if dst_file.exists():
            existing += 1
            continue

        try:
            os.link(src_file, dst_file)
            linked += 1
        except OSError:
            shutil.copy2(src_file, dst_file)

    # Move validation annotation file from val → valid
    if raw_split == "val":
        src_json = BASE / "val" / "_annotations.coco.json"
        dst_json = BASE / "valid" / "_annotations.coco.json"

        if src_json.exists() and not dst_json.exists():
            shutil.move(str(src_json), str(dst_json))

        old_val = BASE / "val"
        if old_val.exists() and not any(old_val.iterdir()):
            old_val.rmdir()

    print(f"{out_split.upper()}:")
    print(f"  Source images : {len(files):,}")
    print(f"  Linked/copied  : {linked:,}")
    print(f"  Already exists : {existing:,}")

print("\nDataset preparation complete.")
print(f"Dataset: {BASE}")
