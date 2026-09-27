from pathlib import Path
import json

BASE = Path(r"D:\projects\Roadsense\data\processed\rfdetr_rdd2022")

SPLITS = ["train", "valid", "test"]
CLASSES = [
    "longitudinal_crack",
    "transverse_crack",
    "alligator_crack",
    "pothole",
]

errors = 0

print("=" * 60)
print("RF-DETR DATASET VALIDATION")
print("=" * 60)

for split in SPLITS:
    folder = BASE / split
    image_dir = folder / "images"
    json_file = folder / "_annotations.coco.json"

    with json_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    images = {x["id"]: x for x in data["images"]}
    annotations = data["annotations"]

    image_files = {
        p.name for p in image_dir.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    }

    missing = 0
    bad_boxes = 0

    for img in data["images"]:
        if img["file_name"] not in image_files:
            missing += 1

    for ann in annotations:
        if ann["image_id"] not in images:
            bad_boxes += 1
            continue

        x, y, w, h = ann["bbox"]
        img = images[ann["image_id"]]

        if (
            w <= 0 or h <= 0 or
            x < 0 or y < 0 or
            x + w > img["width"] + 1 or
            y + h > img["height"] + 1
        ):
            bad_boxes += 1

        if not 0 <= ann["category_id"] < 4:
            bad_boxes += 1

    print(f"\n{split.upper()}")
    print(f"Images in JSON : {len(images):,}")
    print(f"Images on disk : {len(image_files):,}")
    print(f"Annotations    : {len(annotations):,}")
    print(f"Missing images : {missing:,}")
    print(f"Bad annotations: {bad_boxes:,}")

    if missing or bad_boxes:
        errors += missing + bad_boxes

print("\n" + "=" * 60)

if errors == 0:
    print("VALIDATION PASSED")
    print("Dataset is ready for RF-DETR.")
else:
    print(f"VALIDATION FAILED: {errors} problems found.")

print("=" * 60)