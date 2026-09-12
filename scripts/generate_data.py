#!/usr/bin/env python3
"""
SAATHI CLI: Generate and Prepare All Datasets
"""
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml.profile_data import profile_hr_dataset
from ml.create_personnel_master import generate_personnel_master
from ml.generate_synthetic_data import generate_synthetic_longitudinal_data
from ml.prepare_dataset import prepare_integrated_dataset

def main():
    print("==================================================")
    print("SAATHI DATA GENERATION & PREPARATION PIPELINE")
    print("==================================================")
    
    print("\n[Step 1/4] Profiling Official HR Dataset...")
    profile_hr_dataset()

    print("\n[Step 2/4] Generating Personnel Master...")
    generate_personnel_master()

    print("\n[Step 3/4] Generating Synthetic Longitudinal Datasets (12 Months)...")
    generate_synthetic_longitudinal_data()

    print("\n[Step 4/4] Integrating Datasets & Computing Personal Baselines...")
    prepare_integrated_dataset()

    print("\n[✓] All datasets generated, validated, and integrated successfully.")

if __name__ == "__main__":
    main()
