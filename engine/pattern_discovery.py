import numpy as np
import pandas as pd

# Trend Analysis Configuration
RECENT_ANALYSIS_WINDOW_DAYS = 7
MIN_BASELINE_DAYS = 5
MIN_TREND_EFFECT_SIZE = 0.4  # Cohen's d threshold for medium-to-large shifts

# Routine & Correlation Thresholds
SLEEP_CV_STABILITY_THRESHOLD = 0.05  # 5% shift in sleep stability coefficient of variation
CORRELATION_SIGNIFICANCE_THRESHOLD = 0.45  # Pearson correlation strength boundary

def calculate_cohens_d(baseline_series: pd.Series, current_series: pd.Series) -> float:
    """
    Computes Cohen's d to measure the effect size of the shift between
    the baseline period and the current period.

    Args:
        baseline_series (pd.Series): Historical baseline values.
        current_series (pd.Series): Recent observation values.

    Returns:
        float: Calculated effect size. Returns 0.0 for stable/constant inputs.
    """
    baseline_size = len(baseline_series)
    current_size = len(current_series)
    
    if baseline_size <= 1 or current_size <= 1:
        return 0.0
        
    baseline_variance = baseline_series.var(ddof=1)
    current_variance = current_series.var(ddof=1)
    
    # Handle edge case where baseline and current values are perfectly constant
    if baseline_variance == 0 and current_variance == 0:
        return 0.0
        
    pooled_standard_deviation = np.sqrt(
        ((baseline_size - 1) * baseline_variance + (current_size - 1) * current_variance) 
        / (baseline_size + current_size - 2)
    )
    
    if pooled_standard_deviation == 0:
        return 0.0
        
    return (current_series.mean() - baseline_series.mean()) / pooled_standard_deviation


def discover_patterns(behavioral_dataframe: pd.DataFrame) -> list:
    """
    Analyzes user-specific daily observations to discover behavioral patterns and trends.

    Args:
        behavioral_dataframe (pd.DataFrame): Sorted daily observations.

    Returns:
        list: A list of dictionaries representing discovered patterns and correlations.
    """
    discovered_patterns = []
    
    # Process each user profile independently (User Independence Assumption)
    for user_id, user_history_df in behavioral_dataframe.groupby('user_id'):
        user_history_df = user_history_df.sort_values('date')
        total_logged_days = len(user_history_df)
        
        # Enforce Component 4: Evidence Sufficiency - Check minimum days required for patterns
        if total_logged_days < RECENT_ANALYSIS_WINDOW_DAYS:
            continue
            
        # Split into baseline (historical period) and current (recent 7 days)
        baseline_df = user_history_df.iloc[:-RECENT_ANALYSIS_WINDOW_DAYS]
        current_df = user_history_df.iloc[-RECENT_ANALYSIS_WINDOW_DAYS:]
        
        # Abstain from pattern generation if baseline data is insufficient
        if len(baseline_df) < MIN_BASELINE_DAYS:
            continue
            
        # 1. Physical Activity (Steps) Trend Analysis
        steps_cohens_d = calculate_cohens_d(baseline_df['steps'], current_df['steps'])
        if abs(steps_cohens_d) >= MIN_TREND_EFFECT_SIZE:
            baseline_mean = int(round(baseline_df['steps'].mean()))
            current_mean = int(round(current_df['steps'].mean()))
            percentage_change = ((current_mean - baseline_mean) / baseline_mean) * 100
            
            trend_direction = "declined" if steps_cohens_d < 0 else "improved"
            pattern_type = "trend_decline" if steps_cohens_d < 0 else "trend_incline"
            
            discovered_patterns.append({
                'user_id': user_id,
                'metric': 'steps',
                'pattern_type': pattern_type,
                'title': f"Physical activity {trend_direction} over the past week.",
                'evidence': f"Average daily steps changed from {baseline_mean:,} to {current_mean:,} ({percentage_change:+.1f}%).",
                'confidence': float(np.clip(1.0 - np.exp(-abs(steps_cohens_d)), 0.50, 0.98)),
                'raw_details': {
                    'baseline_mean': baseline_mean,
                    'current_mean': current_mean,
                    'cohens_d': steps_cohens_d
                }
            })
            
        # 2. Daily Exercise Duration Trend Analysis
        exercise_cohens_d = calculate_cohens_d(baseline_df['exercise_minutes'], current_df['exercise_minutes'])
        if abs(exercise_cohens_d) >= MIN_TREND_EFFECT_SIZE:
            baseline_mean = int(round(baseline_df['exercise_minutes'].mean()))
            current_mean = int(round(current_df['exercise_minutes'].mean()))
            percentage_change = ((current_mean - baseline_mean) / baseline_mean) * 100 if baseline_mean > 0 else 0
            
            trend_direction = "decreased" if exercise_cohens_d < 0 else "increased"
            pattern_type = "trend_decline" if exercise_cohens_d < 0 else "trend_incline"
            
            discovered_patterns.append({
                'user_id': user_id,
                'metric': 'exercise_minutes',
                'pattern_type': pattern_type,
                'title': f"Daily exercise duration {trend_direction}.",
                'evidence': f"Average daily exercise changed from {baseline_mean} to {current_mean} minutes ({percentage_change:+.1f}%).",
                'confidence': float(np.clip(1.0 - np.exp(-abs(exercise_cohens_d)), 0.50, 0.98)),
                'raw_details': {
                    'baseline_mean': baseline_mean,
                    'current_mean': current_mean,
                    'cohens_d': exercise_cohens_d
                }
            })

        # 3. Sleep Duration Trend Analysis
        sleep_cohens_d = calculate_cohens_d(baseline_df['sleep_hours'], current_df['sleep_hours'])
        if abs(sleep_cohens_d) >= MIN_TREND_EFFECT_SIZE:
            baseline_mean = float(round(baseline_df['sleep_hours'].mean(), 1))
            current_mean = float(round(current_df['sleep_hours'].mean(), 1))
            percentage_change = ((current_mean - baseline_mean) / baseline_mean) * 100
            
            trend_direction = "decreased" if sleep_cohens_d < 0 else "increased"
            pattern_type = "trend_decline" if sleep_cohens_d < 0 else "trend_incline"
            
            discovered_patterns.append({
                'user_id': user_id,
                'metric': 'sleep_hours',
                'pattern_type': pattern_type,
                'title': f"Sleep duration {trend_direction}.",
                'evidence': f"Average daily sleep changed from {baseline_mean} to {current_mean} hours ({percentage_change:+.1f}%).",
                'confidence': float(np.clip(1.0 - np.exp(-abs(sleep_cohens_d)), 0.50, 0.98)),
                'raw_details': {
                    'baseline_mean': baseline_mean,
                    'current_mean': current_mean,
                    'cohens_d': sleep_cohens_d
                }
            })

        # 4. Sleep Routine Consistency (Coefficient of Variation)
        sleep_cv_baseline = (
            baseline_df['sleep_hours'].std() / baseline_df['sleep_hours'].mean() 
            if baseline_df['sleep_hours'].mean() > 0 else 0
        )
        sleep_cv_current = (
            current_df['sleep_hours'].std() / current_df['sleep_hours'].mean() 
            if current_df['sleep_hours'].mean() > 0 else 0
        )
        sleep_cv_difference = sleep_cv_current - sleep_cv_baseline
        
        if abs(sleep_cv_difference) >= SLEEP_CV_STABILITY_THRESHOLD:
            if sleep_cv_difference < 0:
                discovered_patterns.append({
                    'user_id': user_id,
                    'metric': 'sleep_routine',
                    'pattern_type': 'routine_stability',
                    'title': "Sleep routine became more consistent.",
                    'evidence': f"Sleep coefficient of variation decreased from {sleep_cv_baseline*100:.1f}% to {sleep_cv_current*100:.1f}%.",
                    'confidence': float(np.clip(1.0 - sleep_cv_current, 0.50, 0.98)),
                    'raw_details': {'cv_baseline': sleep_cv_baseline, 'cv_current': sleep_cv_current}
                })
            else:
                discovered_patterns.append({
                    'user_id': user_id,
                    'metric': 'sleep_routine',
                    'pattern_type': 'routine_chaos',
                    'title': "Sleep routine became more irregular.",
                    'evidence': f"Sleep coefficient of variation increased from {sleep_cv_baseline*100:.1f}% to {sleep_cv_current*100:.1f}%.",
                    'confidence': float(np.clip(sleep_cv_current + 0.5, 0.50, 0.98)),
                    'raw_details': {'cv_baseline': sleep_cv_baseline, 'cv_current': sleep_cv_current}
                })

        # 5. Deep Work / Productivity Trend Analysis
        deep_work_cohens_d = calculate_cohens_d(baseline_df['deep_work_hours'], current_df['deep_work_hours'])
        if abs(deep_work_cohens_d) >= MIN_TREND_EFFECT_SIZE:
            baseline_mean = float(round(baseline_df['deep_work_hours'].mean(), 1))
            current_mean = float(round(current_df['deep_work_hours'].mean(), 1))
            percentage_change = ((current_mean - baseline_mean) / baseline_mean) * 100
            
            trend_direction = "decreased" if deep_work_cohens_d < 0 else "increased"
            pattern_type = "trend_decline" if deep_work_cohens_d < 0 else "trend_incline"
            
            discovered_patterns.append({
                'user_id': user_id,
                'metric': 'deep_work_hours',
                'pattern_type': pattern_type,
                'title': f"Deep work focus hours {trend_direction}.",
                'evidence': f"Average daily focus changed from {baseline_mean} to {current_mean} hours ({percentage_change:+.1f}%).",
                'confidence': float(np.clip(1.0 - np.exp(-abs(deep_work_cohens_d)), 0.50, 0.98)),
                'raw_details': {
                    'baseline_mean': baseline_mean,
                    'current_mean': current_mean,
                    'cohens_d': deep_work_cohens_d
                }
            })

        # 6. Cross-Metric Correlations (Pearson r)
        # Screen Time vs. Sleep hours
        r_screen_sleep = user_history_df['screen_time_hours'].corr(user_history_df['sleep_hours'])
        if r_screen_sleep <= -CORRELATION_SIGNIFICANCE_THRESHOLD:
            discovered_patterns.append({
                'user_id': user_id,
                'metric': 'screen_time_vs_sleep',
                'pattern_type': 'correlation',
                'title': "High screen time negatively impacts sleep.",
                'evidence': f"Screen time and sleep hours show a negative correlation of r = {r_screen_sleep:.2f}.",
                'confidence': float(abs(r_screen_sleep)),
                'raw_details': {'correlation_coefficient': r_screen_sleep}
            })
            
        # Screen Time vs. Deep Work hours
        r_screen_work = user_history_df['screen_time_hours'].corr(user_history_df['deep_work_hours'])
        if r_screen_work <= -CORRELATION_SIGNIFICANCE_THRESHOLD:
            discovered_patterns.append({
                'user_id': user_id,
                'metric': 'screen_time_vs_deep_work',
                'pattern_type': 'correlation',
                'title': "Screen time is negatively correlating with deep work hours.",
                'evidence': f"Screen time and deep work hours show a negative correlation of r = {r_screen_work:.2f}.",
                'confidence': float(abs(r_screen_work)),
                'raw_details': {'correlation_coefficient': r_screen_work}
            })
            
        # Exercise vs. Deep Work hours (Positive Correlation)
        r_exercise_work = user_history_df['exercise_minutes'].corr(user_history_df['deep_work_hours'])
        if r_exercise_work >= CORRELATION_SIGNIFICANCE_THRESHOLD:
            discovered_patterns.append({
                'user_id': user_id,
                'metric': 'exercise_vs_deep_work',
                'pattern_type': 'correlation',
                'title': "Active exercise habits correlate positively with deep work focus.",
                'evidence': f"Daily exercise minutes and deep work hours show a positive correlation of r = {r_exercise_work:.2f}.",
                'confidence': float(r_exercise_work),
                'raw_details': {'correlation_coefficient': r_exercise_work}
            })

    return discovered_patterns
