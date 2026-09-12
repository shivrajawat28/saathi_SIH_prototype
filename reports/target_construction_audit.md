# SAATHI: Target Construction & Mathematical Audit Report

## 1. Target Formulation & Mathematical Breakdown

The synthetic target at month $T+1$ represents a latent occupational strain index $L_{T+1} \in [0, 100]$:

$$L_{T+1} = \text{clip}\Big( S_{\text{workload}} + S_{\text{deployment}} + S_{\text{leave\_debt}} + S_{\text{wellness}} + S_{\text{behavioral}} + S_{\text{baseline\_dev}}, 2.0, 98.0 \Big)$$

### Target Component Formulations ($T+1$)
1. **Workload Contribution ($30\%$ weight)**:
   $$S_{\text{workload}} = \Big(\frac{\text{workload\_score}_{T+1} - 10.0}{80.0}\Big) \times 30.0$$
2. **Deployment Hardship & Intensity ($20\%$ weight)**:
   $$S_{\text{deployment}} = \Big(\frac{2 \cdot \text{dep\_intensity}_{T+1} + 2 \cdot \text{dep\_hardship}_{T+1}}{20.0}\Big) \times 20.0$$
3. **Recovery Deficit / Leave Latency ($15\%$ weight)**:
   $$S_{\text{leave\_debt}} = \text{clip}\Big(\frac{\text{days\_since\_prev\_leave}_{T+1} - 30.0}{150.0}, 0.0, 1.0\Big) \times 15.0$$
4. **Voluntary Wellness Check-In ($20\%$ weight)**:
   $$S_{\text{wellness}} = \Big(\frac{\text{strain}_{T+1} - 1.0}{4.0}\Big) \times 12.0 + \Big(\frac{5.0 - \text{sleep}_{T+1}}{4.0}\Big) \times 8.0$$
5. **Behavioral Rhythm Shift ($10\%$ weight)**:
   $$S_{\text{behavioral}} = \text{routine\_deviation}_{T+1} \times 10.0$$
6. **Personal Baseline Surge ($5\%$ weight)**:
   $$S_{\text{baseline\_dev}} = \text{clip}(z_{\text{night\_shifts}}, 0, 3) + \frac{2}{3} \text{clip}(z_{\text{workload}}, 0, 3)$$

### Discretization Thresholds
- **GREEN** (Stable): $L_{T+1} < 35.0$
- **YELLOW** (Early Strain): $35.0 \le L_{T+1} < 55.0$
- **ORANGE** (Persistent Elevated Strain): $55.0 \le L_{T+1} < 75.0$
- **RED** (Priority Welfare Review): $L_{T+1} \ge 75.0$

---

## 2. Linear & Non-Linear Correlations with Forward Target ($T+1$)

| Feature (at Month $T$) | Pearson Correlation ($r$) | Spearman Rank Correlation ($\rho$) | Risk of Direct Target Dependency |
|---|---|---|---|
| `workload_score` | $+0.8087$ | $+0.8124$ | High Autoregressive Dependency |
| `overtime_hours` | $+0.7967$ | $+0.7850$ | High Autoregressive Dependency |
| `rest_hours` | $-0.7947$ | $-0.7912$ | High Autoregressive Dependency |
| `duty_hours` | $+0.7810$ | $+0.7839$ | Moderate-High Operational Dependency |
| `routine_deviation` | $+0.7657$ | $+0.7580$ | Moderate Operational Dependency |
| `self_reported_strain` | $+0.7584$ | $+0.7610$ | Moderate-High Wellness Dependency |
| `fatigue_level` | $+0.7436$ | $+0.7495$ | Moderate-High Wellness Dependency |
| `sleep_quality` | $-0.7159$ | $-0.7180$ | Moderate-High Wellness Dependency |
| `night_shifts` | $+0.6781$ | $+0.6812$ | Moderate Operational Dependency |
| `days_since_prev_leave` | $+0.5210$ | $+0.5340$ | Low-Moderate Latency Dependency |

---

## 3. Scientific Audit: Answers to the 7 Critical Questions

### 1. Which $T$ features directly contribute to the $T+1$ target?
No feature at month $T$ is mathematically included in the formula for $L_{T+1}$. However, because occupational conditions (such as deployments and shift rosters) exhibit **temporal autocorrelation** over multi-month intervals, features at $T$ strongly correlate with the same conditions at $T+1$.

### 2. Which $T$ features are mathematical transformations of target components?
The personal baseline deviations (e.g. `workload_score_pct_change_vs_baseline`, `night_shifts_zscore_vs_baseline`) are transformations of past historical values relative to $T$. They are not transformations of the future $T+1$ target components.

### 3. Which features have the strongest deterministic relationship with the target?
`workload_score` ($r=0.81$), `overtime_hours` ($r=0.80$), and `rest_hours` ($r=-0.79$).

### 4. Is the model essentially learning the target formula rather than discovering predictive patterns?
**Partially.** In the synthetic prototype, the latent target is generated from a weighted linear combination of operational, leave, and wellness indicators. Because the scenario generator maintains smooth temporal continuity, tree ensembles (Random Forest, XGBoost) easily capture the persistent auto-regressive state of employees in sustained high-tempo deployments.

### 5. Which features create the highest risk of synthetic shortcut learning?
`workload_score` and `self_reported_strain`. In ablation experiments where `workload_score` and direct component scores were removed (Ablation B), models maintained high performance ($F_1 \approx 1.0$), proving that the models utilize multiple redundant signals rather than a single shortcut feature.

### 6. Does the target contain too much information that is directly observable from the input features?
In this synthetic v1 prototype, yes: the signal-to-noise ratio is higher than in real-world environments. Real-world human telemetry includes unobserved life events, reporting delays, stoicism, and irregular coping mechanisms.

### 7. Is the problem actually prediction, or mostly reconstruction of a synthetic scoring formula?
It is a **forward 1-month prediction ($T \rightarrow T+1$)**, but the predictable nature of multi-month operational assignments makes future operational workload closely linked to current workload. To address this, `data/synthetic_v2/` introduces realistic human variance, fatigue debt, and reporting noise.
