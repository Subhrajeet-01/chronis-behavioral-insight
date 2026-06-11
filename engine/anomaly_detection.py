import numpy as np
import pandas as pd

# Adaptive Rolling Window Config
ROLLING_WINDOW_DAYS = 14
MIN_PERIODS_DAYS = 5

# Metric Fields present in the dataset
METRIC_COLUMNS = [
    'steps',
    'sleep_hours',
    'screen_time_hours',
    'deep_work_hours',
    'exercise_minutes'
]

# Statistical Thresholds
Z_SCORE_ANOMALY_THRESHOLD = 2.0
COMPOUND_Z_SCORE_THRESHOLD = 1.5
EPSILON_DIVISOR = 1e-5

def detect_anomalies(observations_df: pd.DataFrame) -> list:
    """
    Detects unusual daily events or deviations from normal behavior for each user profile.
    Uses rolling statistics to adapt to each user's unique baseline metrics over time.

    Args:
        observations_df (pd.DataFrame): Sorted daily observations containing user activity details.

    Returns:
        list: A list of dictionaries representing detected single-metric and compound anomalies.
    """
    detected_anomalies = []
    
    # Process each user as an independent behavioral system
    for user_id, user_history_df in observations_df.groupby('user_id'):
        user_history_df = user_history_df.sort_values('date').copy()
        total_logged_days = len(user_history_df)
        
        # Ensure we have enough data to calculate baseline statistics
        if total_logged_days < MIN_PERIODS_DAYS:
            continue
            
        # Precompute rolling averages and standard deviations
        # (shifting by 1 day to prevent forward-looking data leakage)
        rolling_averages = {}
        rolling_deviations = {}
        for metric in METRIC_COLUMNS:
            rolling_averages[metric] = (
                user_history_df[metric]
                .shift(1)
                .rolling(window=ROLLING_WINDOW_DAYS, min_periods=MIN_PERIODS_DAYS)
                .mean()
            )
            rolling_deviations[metric] = (
                user_history_df[metric]
                .shift(1)
                .rolling(window=ROLLING_WINDOW_DAYS, min_periods=MIN_PERIODS_DAYS)
                .std()
            )
            
        # Iterate day-by-day to check for deviations against rolling baselines
        for day_index in range(total_logged_days):
            current_day_row = user_history_df.iloc[day_index]
            formatted_date = current_day_row['date'].strftime('%Y-%m-%d')
            
            # 1. Single-Metric Anomaly Checks
            for metric in METRIC_COLUMNS:
                daily_value = current_day_row[metric]
                baseline_mean = rolling_averages[metric].iloc[day_index]
                baseline_std = rolling_deviations[metric].iloc[day_index]
                
                # Skip days where rolling baseline stats are not yet available (NaN)
                if pd.isna(baseline_mean) or pd.isna(baseline_std):
                    continue
                    
                # Epsilon divisor handles constant histories (std = 0) without division-by-zero errors
                deviation_divisor = baseline_std if baseline_std > EPSILON_DIVISOR else EPSILON_DIVISOR
                z_score = (daily_value - baseline_mean) / deviation_divisor
                
                if abs(z_score) >= Z_SCORE_ANOMALY_THRESHOLD:
                    anomaly_direction = "high" if z_score > 0 else "low"
                    
                    # Context-specific description and titles per metric type
                    if metric == 'steps':
                        anomaly_title = "Unusual step count detected." if z_score > 0 else "Significant decline in steps."
                        explanation_text = f"Steps reached {daily_value:,} (rolling average: {int(round(baseline_mean)):,}, deviation: {z_score:+.1f}σ)."
                    elif metric == 'sleep_hours':
                        anomaly_title = "Slept longer than usual." if z_score > 0 else "Severe sleep restriction."
                        explanation_text = f"Sleep duration was {daily_value:.1f} hours (rolling average: {baseline_mean:.1f} hours, deviation: {z_score:+.1f}σ)."
                    elif metric == 'screen_time_hours':
                        anomaly_title = "Screen time spike detected." if z_score > 0 else "Unusually low screen time."
                        explanation_text = f"Screen time was {daily_value:.1f} hours (rolling average: {baseline_mean:.1f} hours, deviation: {z_score:+.1f}σ)."
                    elif metric == 'deep_work_hours':
                        anomaly_title = "High productivity day." if z_score > 0 else "Deep work focus drop."
                        explanation_text = f"Deep work hours were {daily_value:.1f} hours (rolling average: {baseline_mean:.1f} hours, deviation: {z_score:+.1f}σ)."
                    elif metric == 'exercise_minutes':
                        anomaly_title = "Intense exercise session." if z_score > 0 else "Unusually low physical exercise."
                        explanation_text = f"Exercise minutes were {daily_value} mins (rolling average: {int(round(baseline_mean))} mins, deviation: {z_score:+.1f}σ)."
                    else:
                        anomaly_title = f"Anomaly in {metric}."
                        explanation_text = f"Value {daily_value} deviated from rolling average of {baseline_mean:.1f} by {z_score:+.1f}σ."
                        
                    # Calculate confidence scaled linearly with the magnitude of the Z-score
                    confidence_score = float(np.clip(0.70 + (abs(z_score) - Z_SCORE_ANOMALY_THRESHOLD) * 0.15, 0.70, 0.99))
                    
                    detected_anomalies.append({
                        'user_id': user_id,
                        'date': formatted_date,
                        'metric': metric,
                        'anomaly_type': anomaly_direction,
                        'title': anomaly_title,
                        'explanation': explanation_text,
                        'confidence': confidence_score,
                        'raw_details': {
                            'value': float(daily_value),
                            'rolling_mean': float(baseline_mean),
                            'rolling_std': float(baseline_std),
                            'z_score': float(z_score)
                        }
                    })

            # 2. Compound Anomaly Checks (e.g. "Digital Burnout")
            # Defined as high screen time (> 1.5 std) and low sleep (< -1.5 std) simultaneously
            screen_time_val = current_day_row['screen_time_hours']
            screen_time_mean = rolling_averages['screen_time_hours'].iloc[day_index]
            screen_time_std = rolling_deviations['screen_time_hours'].iloc[day_index]
            
            sleep_hours_val = current_day_row['sleep_hours']
            sleep_hours_mean = rolling_averages['sleep_hours'].iloc[day_index]
            sleep_hours_std = rolling_deviations['sleep_hours'].iloc[day_index]
            
            if (not pd.isna(screen_time_mean) and not pd.isna(screen_time_std) and
                not pd.isna(sleep_hours_mean) and not pd.isna(sleep_hours_std)):
                
                screen_time_divisor = screen_time_std if screen_time_std > EPSILON_DIVISOR else EPSILON_DIVISOR
                sleep_hours_divisor = sleep_hours_std if sleep_hours_std > EPSILON_DIVISOR else EPSILON_DIVISOR
                
                screen_time_z_score = (screen_time_val - screen_time_mean) / screen_time_divisor
                sleep_hours_z_score = (sleep_hours_val - sleep_hours_mean) / sleep_hours_divisor
                
                if screen_time_z_score >= COMPOUND_Z_SCORE_THRESHOLD and sleep_hours_z_score <= -COMPOUND_Z_SCORE_THRESHOLD:
                    screen_time_contrib = 0.70 + (screen_time_z_score - COMPOUND_Z_SCORE_THRESHOLD) * 0.15
                    sleep_hours_contrib = 0.70 + (abs(sleep_hours_z_score) - COMPOUND_Z_SCORE_THRESHOLD) * 0.15
                    
                    # Average the confidence contributions and add a compound significance boost
                    combined_confidence = float(np.clip((screen_time_contrib + sleep_hours_contrib) / 2 + 0.05, 0.75, 0.99))
                    
                    detected_anomalies.append({
                        'user_id': user_id,
                        'date': formatted_date,
                        'metric': 'compound_digital_burnout',
                        'anomaly_type': 'compound',
                        'title': "Digital Burnout anomaly detected.",
                        'explanation': (
                            f"Extremely high screen time ({screen_time_val:.1f} hrs, +{screen_time_z_score:.1f}σ) "
                            f"and disrupted sleep ({sleep_hours_val:.1f} hrs, {sleep_hours_z_score:.1f}σ) occurred simultaneously."
                        ),
                        'confidence': combined_confidence,
                        'raw_details': {
                            'screen_time_hours': float(screen_time_val),
                            'screen_time_z_score': float(screen_time_z_score),
                            'sleep_hours': float(sleep_hours_val),
                            'sleep_z_score': float(sleep_hours_z_score)
                        }
                    })

    return detected_anomalies
