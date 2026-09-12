#!/usr/bin/env python3
"""
SAATHI CLI: Evaluate Model Pipeline & Generate Reports
"""
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml.evaluate import evaluate_pipeline

def main():
    print("==================================================")
    print("SAATHI MODEL EVALUATION & FAIRNESS AUDIT")
    print("==================================================")
    evaluate_pipeline()
    print("\n[✓] Evaluation completed successfully.")

if __name__ == "__main__":
    main()
