#!/usr/bin/env python3
"""
SAATHI CLI: Train Model Pipeline
"""
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml.train import train_models

def main():
    print("==================================================")
    print("SAATHI MODEL TRAINING PIPELINE")
    print("==================================================")
    train_models()
    print("\n[✓] Model training completed successfully.")

if __name__ == "__main__":
    main()
