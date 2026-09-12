"""
SAATHI: Personnel Master Data Generator
Extracts deduplicated personnel records from the official HR dataset,
applies pseudonymous identifiers (P-000001 to P-001470),
normalizes core organizational attributes, and outputs data/processed/personnel_master.csv.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from ml.config import OFFICIAL_HR_DIR, PROCESSED_DIR, RANDOM_SEED

def generate_personnel_master():
    csv_path = OFFICIAL_HR_DIR / "HR_Analytics.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Official HR dataset not found at {csv_path}")

    raw_df = pd.read_csv(csv_path)

    # 1. Deduplicate by EmpID (keeping the first occurrence)
    df = raw_df.drop_duplicates(subset=['EmpID'], keep='first').copy()
    df = df.sort_values(by='EmpID').reset_index(drop=True)

    total_personnel = len(df)

    # 2. Assign pseudonymous personnel IDs: P-000001, P-000002, ...
    df['personnel_id'] = [f"P-{i+1:06d}" for i in range(total_personnel)]

    # 3. Select and normalize existing HR attributes
    # Only use columns that exist in the original HR dataset
    hr_columns_map = {
        'personnel_id': 'personnel_id',
        'EmpID': 'original_ref_id',
        'Age': 'age',
        'Gender': 'gender',
        'Department': 'department',
        'JobRole': 'job_role',
        'JobLevel': 'job_level',
        'Education': 'education_level',
        'EducationField': 'education_field',
        'MaritalStatus': 'marital_status',
        'DistanceFromHome': 'distance_from_home',
        'BusinessTravel': 'business_travel',
        'OverTime': 'overtime_eligible',
        'TotalWorkingYears': 'total_working_years',
        'YearsAtCompany': 'years_in_service',
        'YearsInCurrentRole': 'years_in_current_role',
        'YearsSinceLastPromotion': 'years_since_last_promotion',
        'YearsWithCurrManager': 'years_with_curr_supervisor',
        'EnvironmentSatisfaction': 'baseline_env_satisfaction',
        'JobSatisfaction': 'baseline_job_satisfaction',
        'JobInvolvement': 'baseline_job_involvement',
        'WorkLifeBalance': 'baseline_work_life_balance',
        'RelationshipSatisfaction': 'baseline_rel_satisfaction',
        'PerformanceRating': 'performance_rating',
        'TrainingTimesLastYear': 'training_times_last_year',
        'MonthlyIncome': 'monthly_income',
        'PercentSalaryHike': 'percent_salary_hike',
        'NumCompaniesWorked': 'num_prior_organizations',
        'Attrition': 'hr_attrition_historical'
    }

    # Impute missing values for YearsWithCurrManager if any
    median_mgr_years = df['YearsWithCurrManager'].median()
    df['YearsWithCurrManager'] = df['YearsWithCurrManager'].fillna(median_mgr_years)

    selected_df = df[list(hr_columns_map.keys())].rename(columns=hr_columns_map)

    # Save to data/processed/personnel_master.csv
    output_path = PROCESSED_DIR / "personnel_master.csv"
    selected_df.to_csv(output_path, index=False)

    print(f"[✓] Personnel master created successfully: {output_path}")
    print(f"    - Total Unique Personnel: {len(selected_df)}")
    print(f"    - ID Range: {selected_df['personnel_id'].iloc[0]} to {selected_df['personnel_id'].iloc[-1]}")
    return selected_df

if __name__ == "__main__":
    generate_personnel_master()
