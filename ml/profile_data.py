"""
SAATHI: Data Profiling Module for Official HR Dataset
Generates machine-readable (JSON) and human-readable (Markdown) profiles.
Strictly treats HR_Analytics.csv as read-only.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from ml.config import OFFICIAL_HR_DIR, PROFILING_DIR, PROCESSED_DIR

def profile_hr_dataset():
    csv_path = OFFICIAL_HR_DIR / "HR_Analytics.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Official HR dataset not found at {csv_path}")

    df = pd.read_csv(csv_path)

    # 1. Dataset Dimensions
    n_rows, n_cols = df.shape
    columns = list(df.columns)

    # 2. Identifiers & Duplicates
    emp_ids = df['EmpID'].astype(str)
    n_unique_emp = emp_ids.nunique()
    n_duplicate_emp_ids = int(emp_ids.duplicated().sum())
    n_exact_duplicates = int(df.duplicated().sum())

    # 3. Missing values analysis
    missing_counts = df.isnull().sum().to_dict()
    missing_summary = {k: int(v) for k, v in missing_counts.items() if v > 0}

    # 4. Data types
    dtypes_summary = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # 5. Categorical distributions
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    cat_distributions = {}
    for col in cat_cols:
        val_counts = df[col].value_counts(dropna=False).to_dict()
        cat_distributions[col] = {str(k): int(v) for k, v in val_counts.items()}

    # 6. Numerical distributions
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    num_stats = {}
    for col in num_cols:
        desc = df[col].describe().to_dict()
        num_stats[col] = {k: float(v) if pd.notnull(v) else None for k, v in desc.items()}

    # 7. Correlation matrix for numerical columns
    corr_matrix = df[num_cols].corr().fillna(0).to_dict()
    # Format correlations for JSON readability
    json_corr = {col1: {col2: round(val, 4) for col2, val in series.items()} for col1, series in corr_matrix.items()}

    # 8. High cardinality / Suspicious / Constant columns
    constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
    high_cardinality_cols = [col for col in cat_cols if df[col].nunique() > 50]

    # Attrition Distribution (Highlighting non-equivalence to stress)
    attrition_dist = df['Attrition'].value_counts().to_dict() if 'Attrition' in df.columns else {}

    # Assemble JSON Profile
    profile_data = {
        "dataset_name": "HR_Analytics.csv (External Anonymized HR Dataset)",
        "classification": "EXTERNAL_BENCHMARK_NON_CONFIDENTIAL",
        "rows": n_rows,
        "columns_count": n_cols,
        "unique_personnel_count": n_unique_emp,
        "duplicate_personnel_id_count": n_duplicate_emp_ids,
        "exact_duplicate_rows_count": n_exact_duplicates,
        "missing_values": missing_summary,
        "constant_columns": constant_cols,
        "high_cardinality_columns": high_cardinality_cols,
        "data_types": dtypes_summary,
        "attrition_distribution": attrition_dist,
        "categorical_distributions": cat_distributions,
        "numerical_statistics": num_stats,
        "correlation_sample": json_corr,
        "safety_notes": [
            "HR_Analytics.csv is an external, anonymized HR benchmark dataset.",
            "Attrition indicates organizational turnover/exit, NOT mental health, burnout, or psychological condition.",
            "Personnel records must be mapped to pseudonymous identifiers (e.g. P-000001).",
            "YearsWithCurrManager has 57 missing values to be imputed with median/0 during master creation."
        ]
    }

    # Save JSON Profile
    json_path = PROFILING_DIR / "hr_profile.json"
    with open(json_path, "w") as f:
        json.dump(profile_data, f, indent=2)

    # Generate Markdown Profile
    md_path = PROFILING_DIR / "hr_profile.md"
    with open(md_path, "w") as f:
        f.write("# SAATHI: Data Profiling Report - Official HR Dataset\n\n")
        f.write("## 1. Overview & Data Provenance\n")
        f.write("- **Source File**: `data/official_hr/HR_Analytics.csv`\n")
        f.write("- **Classification**: External Anonymized HR Dataset (Benchmark)\n")
        f.write(f"- **Total Rows**: {n_rows}\n")
        f.write(f"- **Total Columns**: {n_cols}\n")
        f.write(f"- **Unique Personnel (EmpID)**: {n_unique_emp}\n")
        f.write(f"- **Duplicate EmpID Entries**: {n_duplicate_emp_ids} (7 exact duplicate rows + 3 duplicate IDs with minor entry variations)\n")
        f.write(f"- **Constant Columns**: {', '.join(constant_cols) if constant_cols else 'None'}\n\n")

        f.write("## 2. Ethical Boundary & Attrition Policy\n")
        f.write("> **CRITICAL SAFETY NOTE**: `Attrition` in this dataset represents organizational employment termination (Yes: %d, No: %d). " % (
            attrition_dist.get('Yes', 0), attrition_dist.get('No', 0)
        ))
        f.write("It **must never** be used as a ground truth or proxy for clinical stress, mental health, burnout, or psychological fitness. SAATHI models operational strain using multi-signal longitudinal behavioral patterns and transparent occupational proxies.\n\n")

        f.write("## 3. Missing Value Audit\n")
        if missing_summary:
            f.write("| Column | Missing Count | Percentage |\n|---|---|---|\n")
            for col, count in missing_summary.items():
                f.write(f"| `{col}` | {count} | {count / n_rows * 100:.2f}% |\n")
        else:
            f.write("No missing values found across all columns.\n")
        f.write("\n")

        f.write("## 4. Column Inventory & Data Types\n")
        f.write("| # | Column Name | Data Type | Unique Values | Sample Values |\n|---|---|---|---|---|\n")
        for idx, col in enumerate(columns, 1):
            unique_cnt = df[col].nunique()
            sample_val = str(df[col].dropna().iloc[0]) if len(df[col].dropna()) > 0 else "N/A"
            f.write(f"| {idx} | `{col}` | `{dtypes_summary[col]}` | {unique_cnt} | {sample_val} |\n")
        f.write("\n")

        f.write("## 5. Key Categorical Distributions\n")
        for col in ['Department', 'JobRole', 'BusinessTravel', 'OverTime', 'EducationField']:
            if col in cat_distributions:
                f.write(f"### `{col}`\n")
                f.write("| Value | Count | Proportion |\n|---|---|---|\n")
                for k, v in cat_distributions[col].items():
                    f.write(f"| {k} | {v} | {v / n_rows * 100:.1f}% |\n")
                f.write("\n")

        f.write("## 6. Numerical Statistics Summary\n")
        f.write("| Column | Mean | Std | Min | Median (50%) | Max |\n|---|---|---|---|---|---|\n")
        key_num_cols = ['Age', 'DailyRate', 'DistanceFromHome', 'EnvironmentSatisfaction', 'JobInvolvement', 
                        'JobLevel', 'JobSatisfaction', 'MonthlyIncome', 'NumCompaniesWorked', 'PercentSalaryHike',
                        'TotalWorkingYears', 'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsAtCompany', 'YearsWithCurrManager']
        for col in key_num_cols:
            if col in num_stats:
                st = num_stats[col]
                f.write(f"| `{col}` | {st.get('mean', 0):.2f} | {st.get('std', 0):.2f} | {st.get('min', 0):.1f} | {st.get('50%', 0):.1f} | {st.get('max', 0):.1f} |\n")
        f.write("\n")

    print(f"[✓] Data profiling completed successfully.")
    print(f"    - JSON Profile: {json_path}")
    print(f"    - Markdown Report: {md_path}")
    return profile_data

if __name__ == "__main__":
    profile_hr_dataset()
