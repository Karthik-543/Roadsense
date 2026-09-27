from pathlib import Path
import shutil

SRC = Path("data/raw/rdd2022")
DST = Path("data/processed/rdd2022")

for split in ["train", "val", "test"]:
    src_img = SRC / split / "images"
    src_lbl = SRC / split / "labels"
    dst_img = DST / split / "images"
    dst_lbl = DST / split / "labels"

    dst_img.mkdir(parents=True, exist_ok=True)
    dst_lbl.mkdir(parents=True, exist_ok=True)

    for img in src_img.iterdir():
        shutil.copy2(img, dst_img / img.name)

    for label in src_lbl.glob("*.txt"):
        output = []

        for line in label.read_text().splitlines():
            parts = line.split()

            if not parts:
                continue

            cls = int(parts[0])

            if cls == 3:
                continue

            if cls == 4:
                parts[0] = "3"

            output.append(" ".join(parts))

        (dst_lbl / label.name).write_text("\n".join(output))

yaml = """path: D:/projects/Roadsense/data/processed/rdd2022
train: train/images
val: val/images
test: test/images

names:
  0: longitudinal_crack
  1: transverse_crack
  2: alligator_crack
  3: pothole
"""

(DST / "data.yaml").write_text(yaml)

print("RDD2022 preprocessing completed.")
print("Output:", DST)