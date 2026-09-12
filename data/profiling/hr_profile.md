# SAATHI: Data Profiling Report - Official HR Dataset

## 1. Overview & Data Provenance
- **Source File**: `data/official_hr/HR_Analytics.csv`
- **Classification**: External Anonymized HR Dataset (Benchmark)
- **Total Rows**: 1480
- **Total Columns**: 38
- **Unique Personnel (EmpID)**: 1470
- **Duplicate EmpID Entries**: 10 (7 exact duplicate rows + 3 duplicate IDs with minor entry variations)
- **Constant Columns**: EmployeeCount, Over18, StandardHours

## 2. Ethical Boundary & Attrition Policy
> **CRITICAL SAFETY NOTE**: `Attrition` in this dataset represents organizational employment termination (Yes: 238, No: 1242). It **must never** be used as a ground truth or proxy for clinical stress, mental health, burnout, or psychological fitness. SAATHI models operational strain using multi-signal longitudinal behavioral patterns and transparent occupational proxies.

## 3. Missing Value Audit
| Column | Missing Count | Percentage |
|---|---|---|
| `YearsWithCurrManager` | 57 | 3.85% |

## 4. Column Inventory & Data Types
| # | Column Name | Data Type | Unique Values | Sample Values |
|---|---|---|---|---|
| 1 | `EmpID` | `object` | 1470 | RM297 |
| 2 | `Age` | `int64` | 43 | 18 |
| 3 | `AgeGroup` | `object` | 5 | 18-25 |
| 4 | `Attrition` | `object` | 2 | Yes |
| 5 | `BusinessTravel` | `object` | 4 | Travel_Rarely |
| 6 | `DailyRate` | `int64` | 886 | 230 |
| 7 | `Department` | `object` | 3 | Research & Development |
| 8 | `DistanceFromHome` | `int64` | 29 | 3 |
| 9 | `Education` | `int64` | 5 | 3 |
| 10 | `EducationField` | `object` | 6 | Life Sciences |
| 11 | `EmployeeCount` | `int64` | 1 | 1 |
| 12 | `EmployeeNumber` | `int64` | 1470 | 405 |
| 13 | `EnvironmentSatisfaction` | `int64` | 4 | 3 |
| 14 | `Gender` | `object` | 2 | Male |
| 15 | `HourlyRate` | `int64` | 71 | 54 |
| 16 | `JobInvolvement` | `int64` | 4 | 3 |
| 17 | `JobLevel` | `int64` | 5 | 1 |
| 18 | `JobRole` | `object` | 9 | Laboratory Technician |
| 19 | `JobSatisfaction` | `int64` | 4 | 3 |
| 20 | `MaritalStatus` | `object` | 3 | Single |
| 21 | `MonthlyIncome` | `int64` | 1349 | 1420 |
| 22 | `SalarySlab` | `object` | 4 | Upto 5k |
| 23 | `MonthlyRate` | `int64` | 1427 | 25233 |
| 24 | `NumCompaniesWorked` | `int64` | 10 | 1 |
| 25 | `Over18` | `object` | 1 | Y |
| 26 | `OverTime` | `object` | 2 | No |
| 27 | `PercentSalaryHike` | `int64` | 15 | 13 |
| 28 | `PerformanceRating` | `int64` | 2 | 3 |
| 29 | `RelationshipSatisfaction` | `int64` | 4 | 3 |
| 30 | `StandardHours` | `int64` | 1 | 80 |
| 31 | `StockOptionLevel` | `int64` | 4 | 0 |
| 32 | `TotalWorkingYears` | `int64` | 40 | 0 |
| 33 | `TrainingTimesLastYear` | `int64` | 7 | 2 |
| 34 | `WorkLifeBalance` | `int64` | 4 | 3 |
| 35 | `YearsAtCompany` | `int64` | 37 | 0 |
| 36 | `YearsInCurrentRole` | `int64` | 19 | 0 |
| 37 | `YearsSinceLastPromotion` | `int64` | 16 | 0 |
| 38 | `YearsWithCurrManager` | `float64` | 18 | 0.0 |

## 5. Key Categorical Distributions
### `Department`
| Value | Count | Proportion |
|---|---|---|
| Research & Development | 967 | 65.3% |
| Sales | 450 | 30.4% |
| Human Resources | 63 | 4.3% |

### `JobRole`
| Value | Count | Proportion |
|---|---|---|
| Sales Executive | 329 | 22.2% |
| Research Scientist | 293 | 19.8% |
| Laboratory Technician | 261 | 17.6% |
| Manufacturing Director | 147 | 9.9% |
| Healthcare Representative | 132 | 8.9% |
| Manager | 102 | 6.9% |
| Sales Representative | 84 | 5.7% |
| Research Director | 80 | 5.4% |
| Human Resources | 52 | 3.5% |

### `BusinessTravel`
| Value | Count | Proportion |
|---|---|---|
| Travel_Rarely | 1042 | 70.4% |
| Travel_Frequently | 279 | 18.9% |
| Non-Travel | 151 | 10.2% |
| TravelRarely | 8 | 0.5% |

### `OverTime`
| Value | Count | Proportion |
|---|---|---|
| No | 1062 | 71.8% |
| Yes | 418 | 28.2% |

### `EducationField`
| Value | Count | Proportion |
|---|---|---|
| Life Sciences | 607 | 41.0% |
| Medical | 470 | 31.8% |
| Marketing | 161 | 10.9% |
| Technical Degree | 132 | 8.9% |
| Other | 83 | 5.6% |
| Human Resources | 27 | 1.8% |

## 6. Numerical Statistics Summary
| Column | Mean | Std | Min | Median (50%) | Max |
|---|---|---|---|---|---|
| `Age` | 36.92 | 9.13 | 18.0 | 36.0 | 60.0 |
| `DailyRate` | 801.38 | 403.13 | 102.0 | 800.0 | 1499.0 |
| `DistanceFromHome` | 9.22 | 8.13 | 1.0 | 7.0 | 29.0 |
| `EnvironmentSatisfaction` | 2.72 | 1.09 | 1.0 | 3.0 | 4.0 |
| `JobInvolvement` | 2.73 | 0.71 | 1.0 | 3.0 | 4.0 |
| `JobLevel` | 2.06 | 1.11 | 1.0 | 2.0 | 5.0 |
| `JobSatisfaction` | 2.73 | 1.10 | 1.0 | 3.0 | 4.0 |
| `MonthlyIncome` | 6504.99 | 4700.26 | 1009.0 | 4933.0 | 19999.0 |
| `NumCompaniesWorked` | 2.69 | 2.49 | 0.0 | 2.0 | 9.0 |
| `PercentSalaryHike` | 15.21 | 3.66 | 11.0 | 14.0 | 25.0 |
| `TotalWorkingYears` | 11.28 | 7.77 | 0.0 | 10.0 | 40.0 |
| `TrainingTimesLastYear` | 2.80 | 1.29 | 0.0 | 3.0 | 6.0 |
| `WorkLifeBalance` | 2.76 | 0.71 | 1.0 | 3.0 | 4.0 |
| `YearsAtCompany` | 7.01 | 6.12 | 0.0 | 5.0 | 40.0 |
| `YearsWithCurrManager` | 4.12 | 3.56 | 0.0 | 3.0 | 17.0 |

