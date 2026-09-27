from pathlib import Path
import json
from PIL import Image

RAW = Path(r"D:\projects\Roadsense\data\raw\rdd2022")
OUT = Path(r"D:\projects\Roadsense\data\processed\rfdetr_rdd2022")

CLASSES = [
    "longitudinal_crack",
    "transverse_crack",
    "alligator_crack",
    "pothole",
]

# Original RDD2022 → our 4-class dataset
CLASS_MAP = {
    0: 0,
    1: 1,
    2: 2,
    4: 3,
}

total_images = 0
total_annotations = 0
discarded = 0
invalid = 0
class_counts = [0] * 4


def convert_split(split):
    global total_images, total_annotations, discarded, invalid

    image_dir = RAW / split / "images"
    label_dir = RAW / split / "labels"

    out_dir = OUT / split
    out_dir.mkdir(parents=True, exist_ok=True)

    images = []
    annotations = []
    ann_id = 1

    image_files = sorted(
        p for p in image_dir.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )

    for image_id, image_path in enumerate(image_files, start=1):
        total_images += 1

        try:
            with Image.open(image_path) as im:
                width, height = im.size
        except Exception as e:
            print(f"INVALID IMAGE: {image_path} -> {e}")
            invalid += 1
            continue

        images.append({
            "id": image_id,
            "file_name": image_path.name,
            "width": width,
            "height": height
        })

        label_path = label_dir / f"{image_path.stem}.txt"

        if not label_path.exists():
            continue

        for line in label_path.read_text().splitlines():
            parts = line.split()

            if len(parts) != 5:
                invalid += 1
                continue

            try:
                old_cls = int(parts[0])
                xc, yc, bw, bh = map(float, parts[1:])
            except ValueError:
                invalid += 1
                continue

            # Remove original class 3
            if old_cls == 3:
                discarded += 1
                continue

            # Ignore unexpected classes
            if old_cls not in CLASS_MAP:
                invalid += 1
                continue

            # Validate normalized YOLO coordinates
            if not (
                0 <= xc <= 1 and
                0 <= yc <= 1 and
                0 < bw <= 1 and
                0 < bh <= 1
            ):
                invalid += 1
                continue

            new_cls = CLASS_MAP[old_cls]

            # YOLO normalized → COCO pixel coordinates
            x = (xc - bw / 2) * width
            y = (yc - bh / 2) * height
            w = bw * width
            h = bh * height

            # Clip to image boundaries
            x = max(0, min(x, width))
            y = max(0, min(y, height))
            w = min(w, width - x)
            h = min(h, height - y)

            if w <= 0 or h <= 0:
                invalid += 1
                continue

            annotations.append({
                "id": ann_id,
                "image_id": image_id,
                "category_id": new_cls,
                "bbox": [x, y, w, h],
                "area": w * h,
                "iscrowd": 0
            })

            class_counts[new_cls] += 1
            total_annotations += 1
            ann_id += 1

    # RF-DETR/COCO annotation file
    coco = {
        "info": {
            "description": "RoadSense RDD2022 4-class dataset"
        },
        "licenses": [],
        "images": images,
        "annotations": annotations,
        "categories": [
            {
                "id": i,
                "name": name,
                "supercategory": "road_damage"
            }
            for i, name in enumerate(CLASSES)
        ]
    }

    json_path = out_dir / "_annotations.coco.json"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(coco, f)

    print(f"\n{split.upper()}")
    print(f"Images:      {len(images):,}")
    print(f"Annotations: {len(annotations):,}")
    print(f"Saved:       {json_path}")


print("=" * 60)
print("RoadSense RDD2022 → RF-DETR COCO CONVERSION")
print("=" * 60)

for split in ["train", "val", "test"]:
    convert_split(split)

print("\n" + "=" * 60)
print("FINAL REPORT")
print("=" * 60)
print(f"Total images:       {total_images:,}")
print(f"Total annotations:  {total_annotations:,}")
print(f"Discarded class 3:  {discarded:,}")
print(f"Invalid annotations:{invalid:,}")

print("\nClass counts:")
for i, name in enumerate(CLASSES):
    print(f"{i}: {name:20s} {class_counts[i]:,}")

print("\nOutput:")
print(OUT)
print("=" * 60)