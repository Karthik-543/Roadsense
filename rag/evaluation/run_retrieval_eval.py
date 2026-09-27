import json
from pathlib import Path
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from retrieval.evidence_retriever import retrieve

BASE = Path(__file__).resolve().parent
QUERIES = BASE / "queries.json"
RESULTS = BASE / "results"

RESULTS.mkdir(exist_ok=True)

with open(QUERIES, encoding="utf-8") as f:
    queries = json.load(f)

results = []

for item in queries:
    print(f"Running {item['id']}: {item['query']}")

    evidence = retrieve(item["query"], k=5)

    results.append({
        "id": item["id"],
        "query": item["query"],
        "type": item["type"],
        "evidence": evidence
    })

output = RESULTS / "baseline_retrieval.json"

with open(output, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\nEvaluation complete.")
print(f"Queries: {len(results)}")
print(f"Saved: {output}")