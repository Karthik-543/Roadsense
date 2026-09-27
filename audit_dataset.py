from pathlib import Path
from collections import Counter

root = Path("data/raw/rdd2022")
counts = Counter()

for f in root.rglob("*.txt"):
    for line in f.read_text().splitlines():
        p = line.split()
        if p:
            counts[p[0]] += 1

print("=" * 40)
print("RDD2022 CLASS DISTRIBUTION")
print("=" * 40)

for c, n in sorted(counts.items(), key=lambda x: int(x[0])):
    print(f"Class {c}: {n}")

print(f"\nTotal annotations: {sum(counts.values())}")