"""
SAATHI: Personal Baseline Engine Unit Tests
"""

import pytest
import pandas as pd
import numpy as np
from ml.baseline.personal_baseline import PersonalBaselineEngine

def test_baseline_engine_basic_computation():
    # Construct a minimal toy longitudinal dataset for 2 personnel across 5 periods
    records = []
    for pid in ["P-000001", "P-000002"]:
        for m in range(1, 6):
            duty_hrs = 160 + m * 10 if pid == "P-000001" else 180
            records.append({
                "personnel_id": pid,
                "month_idx": m,
                "duty_hours": duty_hrs,
                "night_shifts": m
            })
    
    df = pd.DataFrame(records)
    engine = PersonalBaselineEngine(min_history_periods=3, window_size=3)
    result = engine.compute_personnel_baselines(
        df,
        metric_cols=["duty_hours", "night_shifts"],
        personnel_id_col="personnel_id",
        time_col="month_idx"
    )

    assert "duty_hours_personal_mean" in result.columns
    assert "duty_hours_pct_change_vs_baseline" in result.columns
    assert "duty_hours_zscore_vs_baseline" in result.columns
    assert "baseline_available" in result.columns

    # First period should have baseline_available = False
    p1_first_month = result[(result['personnel_id'] == "P-000001") & (result['month_idx'] == 1)].iloc[0]
    assert p1_first_month['baseline_available'] == False

    # 4th period should have baseline_available = True (>= 3 periods of history)
    p1_fourth_month = result[(result['personnel_id'] == "P-000001") & (result['month_idx'] == 4)].iloc[0]
    assert p1_fourth_month['baseline_available'] == True

    # Check shift: Period 2 baseline mean should equal Period 1 value (170)
    p1_second_month = result[(result['personnel_id'] == "P-000001") & (result['month_idx'] == 2)].iloc[0]
    assert p1_second_month['duty_hours_personal_mean'] == 170.0
