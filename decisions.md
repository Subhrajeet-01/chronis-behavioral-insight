# Chronis Behavioral Insight Engine — Decisions & Methodology

This document outlines the architectural decisions, mathematical methodology, assumptions, and failure modes for the Chronis Behavioral Insight Engine.

---

## 1. Core Methodology

### Component 1 — Pattern Discovery
To identify long-horizon behavioral trends, the system operates on an individual profile basis using three primary analysis techniques:

1.  **Temporal Trends (Cohen's d Effect Size)**:
    *   The system compares the recent 7-day window (current period) against preceding historical logs (baseline period).
    *   The mean difference $\Delta = \mu_{\text{current}} - \mu_{\text{baseline}}$ is determined, and the standardized effect size is calculated via Cohen's d:
        $$d = \frac{|\mu_{\text{current}} - \mu_{\text{baseline}}|}{\sigma_{\text{pooled}}}$$
    *   A standardized difference of $|d| \ge 0.40$ is classified as a significant behavioral trend.

2.  **Cross-Metric Correlations**:
    *   The Pearson correlation coefficient ($r$) is calculated between daily metric pairs (e.g., `screen_time_hours` and `sleep_hours`) across the entire history.
    *   An absolute correlation value $|r| \ge 0.45$ triggers an association claim (e.g., elevated screen time correlating with reduced sleep duration).

3.  **Routine Consistency**:
    *   The Coefficient of Variation ($CV = \sigma / \mu$) is evaluated for sleep and deep work duration to measure scheduling volatility.
    *   A decreasing $CV$ over time indicates progress toward routine stability.

---

### Component 2 — Anomaly Detection
Daily anomalies are identified using rolling statistical boundaries rather than fixed global limits, enabling the engine to adjust to each user's unique baseline:

*   **Z-Score Outliers**: A daily observation $x_t$ is flagged if its deviation from the preceding 14-day rolling mean ($\mu_{t-1}$) and standard deviation ($\sigma_{t-1}$) exceeds a critical boundary:
    $$Z_t = \frac{x_t - \mu_{t-1}}{\sigma_{t-1}}$$
    An anomaly is triggered if $|Z_t| \ge 2.0$.
*   **Compound Anomalies**: The engine detects co-occurring distress indicators, specifically **"Digital Burnout"**, defined as simultaneous occurrences of high screen time ($Z \ge 1.5$) and low sleep duration ($Z \le -1.5$) on the same day.
*   **Explainability**: Every flagged anomaly is saved with descriptive details detailing the exact percentage or standard deviation change relative to that profile's baseline.

---

### Component 3 — Insight Generation & Confidence Scoring
Every generated insight contains:
1.  **The Insight Statement**: A clear, natural language summary.
2.  **Evidence**: Precise statistics (e.g., baseline vs. current averages, correlation values, and percentage changes).
3.  **Confidence Score**: A value between $0.0$ and $1.0$ computed as follows:
    *   *For Trends*: $C = 1.0 - e^{-|d|}$, where $d$ is Cohen's d. This maps confidence non-linearly to the magnitude of the behavioral shift.
    *   *For Correlations*: $C = |r|$, directly reflecting the strength of the linear association.
    *   *For Routine Strength*: $C = 1.0 - CV_{\text{current}}$, representing predictability.

---

### Component 4 — Evidence Sufficiency (Abstention Engine)
The engine prioritizes accuracy and clinical safety over output volume. Candidate claims are withheld under the following conditions:
1.  **Insufficient Data**: The user profile has fewer than 7 days of records.
2.  **Weak Signal**: The computed confidence score is below the 70% threshold ($C < 0.70$).
3.  **Baseline Ambiguity**: Contradictory behavior (such as increasing sleep duration coupled with a massive spike in sleep variance) suspends routine trend reporting.

---

## 2. Key Assumptions
*   **Daily Continuity**: Daily logs are assumed to be contiguous. Missing values are filled using localized imputation, but data blocks with gaps exceeding 3 consecutive days trigger pipeline abstention for the affected window.
*   **Profile Autonomy**: Each user profile is treated as an independent closed behavioral system. An anomaly or trend is calculated strictly relative to that user's own baseline, preventing population averages from distorting individual insights.
*   **Baseline Representation**: A sustained change over 7+ days is assumed to be a genuine baseline trend shift rather than a series of daily anomalies.

---

## 3. Failure Modes & Mitigations

| Failure Mode | Description | Mitigation |
| :--- | :--- | :--- |
| **Outlier Contamination** | A single extreme value (e.g., 25,000 steps) skewing rolling metrics and generating false subsequent anomalies. | The engine bounds standard deviation dividers using `EPSILON_DIVISOR` and checks rolling averages to prevent baseline skewing. |
| **Gradual Trend Drift** | A slow decline in activity over months failing to trigger daily anomaly alerts. | The long-horizon trend analysis (Component 1) compares historical baseline blocks to current blocks, capturing slow, continuous shifts. |
| **Cold Start Problem** | Calculations fail or return errors for new profiles without sufficient history. | The pipeline automatically suspends processing for any profile with fewer than 7 days of observations. |
| **Spurious Correlations** | Non-causal associations occurring by chance (e.g., random alignment between steps and screen time). | Analysis is constrained strictly to predefined, physiologically and behaviorally relevant pairs (e.g., screen time vs. sleep, exercise vs. deep work). |
