import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

def main():
    print("\n" + "=" * 70)
    print("STARTING ROADSENSE AI BENCHMARK EXECUTION PIPELINE")
    print("=" * 70)

    import evaluation.evaluate_all
    evaluation.evaluate_all.main()

    import evaluation.ablation_study
    evaluation.ablation_study.run_ablation()

    print("\nALL EVALUATION EXPERIMENTS & ABLATION STUDIES COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    main()
