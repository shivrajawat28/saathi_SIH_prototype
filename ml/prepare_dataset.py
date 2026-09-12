"""
SAATHI: Dataset Preparation & Feature Engineering Pipeline
Integrates Personnel Master, Deployment, Leave, Workload, Wellness, and Behavioral records.
Computes personal baseline statistics, temporal lags, and constructs the non-leaking T+1 target.
Outputs data/processed/integrated_longitudinal.parquet and .csv.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from ml.config import (
    PROCESSED_DIR,
    SYNTHETIC_DIR,
    RANDOM_SEED,
    SCORE_THRESHOLDS
)
from ml.baseline.personal_baseline import PersonalBaselineEngine

def prepare_integrated_dataset():
    # 1. Load all component datasets
    personnel_df = pd.read_csv(PROCESSED_DIR / "personnel_master.csv")
    dep_df = pd.read_csv(SYNTHETIC_DIR / "deployment" / "deployment_records.csv")
    leave_df = pd.read_csv(SYNTHETIC_DIR / "leave" / "leave_history.csv")
    workload_df = pd.read_csv(SYNTHETIC_DIR / "workload" / "workload_records.csv")
    wellness_df = pd.read_csv(SYNTHETIC_DIR / "wellness" / "wellness_surveys.csv")
    behavioral_df = pd.read_csv(SYNTHETIC_DIR / "behavioral" / "behavioral_records.csv")

    print("[*] Merging longitudinal records across 1,470 personnel and 12 periods...")

    # 2. Merge Workload, Wellness, and Behavioral records by [personnel_id, month_idx, date]
    longitudinal_df = workload_df.merge(
        wellness_df.drop(columns=['date'], errors='ignore'),
        on=['personnel_id', 'month_idx'],
        how='left'
    )
    longitudinal_df = longitudinal_df.merge(
        behavioral_df.drop(columns=['date'], errors='ignore'),
        on=['personnel_id', 'month_idx'],
        how='left'
    )

    # 3. Merge Deployment information (aggregated per personnel-month)
    dep_agg = dep_df.groupby(['personnel_id', 'month_idx']).agg(
        is_deployed=('deployment_id', 'count'),
        dep_duration_days=('deployment_duration_days', 'sum'),
        dep_intensity=('operational_intensity', 'max'),
        dep_hardship=('hardship_level', 'max'),
        dep_recovery_required=('recovery_required', 'max'),
        dep_type=('deployment_type', 'first'),
        dep_location=('location_category', 'first')
    ).reset_index()

    longitudinal_df = longitudinal_df.merge(dep_agg, on=['personnel_id', 'month_idx'], how='left')
    longitudinal_df['is_deployed'] = longitudinal_df['is_deployed'].fillna(0).astype(int)
    longitudinal_df['dep_duration_days'] = longitudinal_df['dep_duration_days'].fillna(0).astype(int)
    longitudinal_df['dep_intensity'] = longitudinal_df['dep_intensity'].fillna(1).astype(int)
    longitudinal_df['dep_hardship'] = longitudinal_df['dep_hardship'].fillna(1).astype(int)
    longitudinal_df['dep_recovery_required'] = longitudinal_df['dep_recovery_required'].fillna(False).astype(bool)
    longitudinal_df['dep_type'] = longitudinal_df['dep_type'].fillna('None')
    longitudinal_df['dep_location'] = longitudinal_df['dep_location'].fillna('Base')

    # 4. Merge Leave history (aggregated per personnel-month)
    leave_agg = leave_df.groupby(['personnel_id', 'month_idx']).agg(
        took_leave=('leave_id', 'count'),
        leave_duration_days=('duration_days', 'sum'),
        leave_type=('leave_type', 'first'),
        days_since_prev_leave=('days_since_previous_leave', 'min')
    ).reset_index()

    longitudinal_df = longitudinal_df.merge(leave_agg, on=['personnel_id', 'month_idx'], how='left')
    longitudinal_df['took_leave'] = longitudinal_df['took_leave'].fillna(0).astype(int)
    longitudinal_df['leave_duration_days'] = longitudinal_df['leave_duration_days'].fillna(0).astype(int)
    longitudinal_df['leave_type'] = longitudinal_df['leave_type'].fillna('None')
    
    # Forward-fill days_since_prev_leave across months per personnel
    longitudinal_df = longitudinal_df.sort_values(by=['personnel_id', 'month_idx']).reset_index(drop=True)
    longitudinal_df['days_since_prev_leave'] = longitudinal_df.groupby('personnel_id')['days_since_prev_leave'].ffill().bfill().fillna(45).astype(int)

    # 5. Merge static Personnel Master attributes
    merged_df = longitudinal_df.merge(personnel_df, on='personnel_id', how='left')

    # 6. Apply Personal Baseline Engine
    print("[*] Computing personalized rolling baselines and deviations...")
    baseline_metrics = [
        'duty_hours', 'overtime_hours', 'night_shifts', 'consecutive_duty_days',
        'rest_hours', 'workload_score', 'sleep_quality', 'fatigue_level', 'self_reported_strain'
    ]
    baseline_engine = PersonalBaselineEngine(min_history_periods=3, window_size=4)
    df_with_baselines = baseline_engine.compute_personnel_baselines(
        merged_df,
        metric_cols=baseline_metrics,
        personnel_id_col='personnel_id',
        time_col='month_idx'
    )

    # 7. Construct Transparent Multi-Signal Latent Strain Index at each month T
    # Score calculation formula (transparent proxy)
    strain_workload = ((df_with_baselines['workload_score'] - 10.0) / 80.0) * 30.0
    strain_dep = ((df_with_baselines['dep_intensity'] * 2.0 + df_with_baselines['dep_hardship'] * 2.0) / 20.0) * 20.0
    strain_leave_debt = np.clip((df_with_baselines['days_since_prev_leave'] - 30.0) / 150.0, 0.0, 1.0) * 15.0
    
    # Wellness contribution (handled with fallback if check-in was skipped)
    survey_strain = df_with_baselines['self_reported_strain'].fillna(2.5)
    survey_sleep = df_with_baselines['sleep_quality'].fillna(3.5)
    strain_wellness = (((survey_strain - 1.0) / 4.0) * 12.0) + (((5.0 - survey_sleep) / 4.0) * 8.0)
    
    # Behavioral deviation contribution
    strain_behavioral = df_with_baselines['routine_deviation'] * 10.0
    
    # Baseline deviation contribution (zscore of night shifts and workload)
    z_ns = df_with_baselines['night_shifts_zscore_vs_baseline'].clip(0, 3.0) / 3.0
    z_wl = df_with_baselines['workload_score_zscore_vs_baseline'].clip(0, 3.0) / 3.0
    strain_baseline_dev = (z_ns * 3.0 + z_wl * 2.0)

    latent_score = np.clip(
        strain_workload + strain_dep + strain_leave_debt + strain_wellness + strain_behavioral + strain_baseline_dev,
        2.0, 98.0
    )

    df_with_baselines['period_latent_strain_score'] = latent_score.round(1)
    
    # Map score to category
    def map_score_to_priority(score):
        if score < 35.0:
            return "GREEN"
        elif score < 55.0:
            return "YELLOW"
        elif score < 75.0:
            return "ORANGE"
        else:
            return "RED"

    df_with_baselines['period_support_priority'] = df_with_baselines['period_latent_strain_score'].apply(map_score_to_priority)

    # 8. Create NON-LEAKING Forward Target (T+1 Horizon)
    # Target for row at month T is the welfare status at month T+1
    print("[*] Creating non-leaking predictive target at horizon T+1...")
    df_sorted = df_with_baselines.sort_values(by=['personnel_id', 'month_idx']).reset_index(drop=True)
    
    df_sorted['target_support_priority_next_month'] = df_sorted.groupby('personnel_id')['period_support_priority'].shift(-1)
    df_sorted['target_support_score_next_month'] = df_sorted.groupby('personnel_id')['period_latent_strain_score'].shift(-1)

    # Compute Data Completeness Score (0.0 to 1.0)
    key_signal_cols = [
        'duty_hours', 'overtime_hours', 'night_shifts', 'rest_hours',
        'sleep_quality', 'fatigue_level', 'self_reported_strain', 'routine_deviation'
    ]
    df_sorted['data_completeness'] = (1.0 - (df_sorted[key_signal_cols].isnull().sum(axis=1) / len(key_signal_cols))).round(2)

    # Save Output
    output_csv = PROCESSED_DIR / "integrated_longitudinal.csv"
    output_parquet = PROCESSED_DIR / "integrated_longitudinal.parquet"
    
    df_sorted.to_csv(output_csv, index=False)
    df_sorted.to_parquet(output_parquet, index=False)

    print(f"[✓] Integrated dataset successfully created:")
    print(f"    - Total Rows: {len(df_sorted)} ({df_sorted['personnel_id'].nunique()} personnel x 12 months)")
    print(f"    - CSV Path: {output_csv}")
    print(f"    - Parquet Path: {output_parquet}")
    print(f"    - Columns: {len(df_sorted.columns)}")
    print(f"    - Next-Month Target Distribution (Months 1-11):")
    print(df_sorted['target_support_priority_next_month'].value_counts(dropna=False))

    return df_sorted

if __name__ == "__main__":
    prepare_integrated_dataset()
