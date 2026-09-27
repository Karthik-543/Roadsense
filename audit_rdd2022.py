from pathlib import Path
from collections import Counter

root = Path("data/raw/rdd2022")

for split in ["train", "val", "test"]:
    labels = root / split / "labels"
    images = root / split / "images"

    counts = Counter()

    for file in labels.glob("*.txt"):
        for line in file.read_text().splitlines():
            if line.strip():
                counts[int(line.split()[0])] += 1

    print(f"\n{split.upper()}")
    print("Images:", len(list(images.glob("*"))))
    print("Labels:", len(list(labels.glob("*.txt"))))
    print("Classes:", dict(sorted(counts.items())))