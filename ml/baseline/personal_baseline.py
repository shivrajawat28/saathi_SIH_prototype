"""
SAATHI: Personal Baseline Engine
Computes individualized rolling statistics, deviations, z-scores, and trends.
Distinguishes personal norm changes from generic population-wide cutoffs.
Provides cold-start fallback with confidence calibration.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

class PersonalBaselineEngine:
    """
    Engine to compute personalized baseline parameters for longitudinal personnel metrics.
    """
    def __init__(self, min_history_periods: int = 3, window_size: int = 4):
        self.min_history_periods = min_history_periods
        self.window_size = window_size
        self.population_priors: Dict[str, Dict[str, float]] = {}

    def fit_population_priors(self, df: pd.DataFrame, metric_cols: List[str]):
        """
        Fit population-wide fallback priors for cold-start personnel.
        """
        for col in metric_cols:
            if col in df.columns:
                series = pd.to_numeric(df[col], errors='coerce').dropna()
                self.population_priors[col] = {
                    'mean': float(series.mean()) if len(series) > 0 else 0.0,
                    'std': float(series.std()) if len(series) > 1 and series.std() > 0 else 1.0,
                    'median': float(series.median()) if len(series) > 0 else 0.0
                }

    def compute_personnel_baselines(
        self,
        df: pd.DataFrame,
        metric_cols: List[str],
        personnel_id_col: str = "personnel_id",
        time_col: str = "month_idx"
    ) -> pd.DataFrame:
        """
        Computes rolling personal baseline statistics up to period T-1 (excluding current period T to prevent leakage)
        and calculates relative deviation, z-scores, and trends.
        """
        df_sorted = df.sort_values(by=[personnel_id_col, time_col]).copy()
        
        # Fit priors if not already fitted
        if not self.population_priors:
            self.fit_population_priors(df_sorted, metric_cols)

        result_dfs = []

        # Group by individual personnel
        for pid, group in df_sorted.groupby(personnel_id_col, sort=False):
            group_copy = group.copy()
            n_rows = len(group_copy)
            
            # Baseline availability indicator
            group_copy['baseline_available'] = [i >= self.min_history_periods for i in range(n_rows)]
            group_copy['history_periods_count'] = list(range(n_rows))

            for col in metric_cols:
                if col not in group_copy.columns:
                    continue
                
                vals = pd.to_numeric(group_copy[col], errors='coerce')
                
                # Shift by 1 so period T baseline ONLY uses past history T-1, T-2, ...
                shifted_vals = vals.shift(1)
                
                # Expanding / Rolling mean and std over prior periods
                roll_mean = shifted_vals.rolling(window=self.window_size, min_periods=1).mean()
                roll_std = shifted_vals.rolling(window=self.window_size, min_periods=1).std().fillna(1.0)
                roll_std = roll_std.apply(lambda s: max(s, 0.5)) # Prevent division by zero
                roll_median = shifted_vals.rolling(window=self.window_size, min_periods=1).median()

                # Prior fallback for period 0 (first period has no prior history)
                prior_mean = self.population_priors.get(col, {}).get('mean', 0.0)
                prior_std = self.population_priors.get(col, {}).get('std', 1.0)

                roll_mean = roll_mean.fillna(prior_mean)
                roll_std = roll_std.fillna(prior_std)
                roll_median = roll_median.fillna(prior_mean)

                # Store baseline features
                group_copy[f'{col}_personal_mean'] = roll_mean.round(2)
                group_copy[f'{col}_personal_std'] = roll_std.round(2)
                group_copy[f'{col}_personal_median'] = roll_median.round(2)

                # Deviation features:
                # 1. Delta from personal mean
                group_copy[f'{col}_delta_vs_baseline'] = (vals - roll_mean).round(2)
                
                # 2. Percentage deviation (relative change)
                pct_change = ((vals - roll_mean) / (roll_mean.abs() + 1e-4)) * 100.0
                group_copy[f'{col}_pct_change_vs_baseline'] = pct_change.clip(-200.0, 300.0).round(2)

                # 3. Z-score relative to personal variation
                z_score = (vals - roll_mean) / roll_std
                group_copy[f'{col}_zscore_vs_baseline'] = z_score.clip(-4.0, 4.0).round(2)

                # 4. Short-term Trend (Current vs shifted 1 period)
                group_copy[f'{col}_lag1_diff'] = (vals - shifted_vals).fillna(0.0).round(2)

            result_dfs.append(group_copy)

        combined_df = pd.concat(result_dfs, ignore_index=True)
        return combined_df
