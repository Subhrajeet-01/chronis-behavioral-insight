import pytest
import pandas as pd
import numpy as np
from engine.anomaly_detection import detect_anomalies

def test_detect_single_metric_anomaly():
    # 20 days of data: 19 stable days, 1 extreme drop in steps on the 20th day
    dates = pd.date_range(start='2026-01-01', periods=20)
    steps_data = [8000] * 19 + [500]  
    
    user_behavior_dataframe = pd.DataFrame({
        'user_id': ['U1'] * 20,
        'date': dates,
        'steps': steps_data,
        'sleep_hours': [7.0] * 20,
        'screen_time_hours': [4.0] * 20,
        'deep_work_hours': [3.0] * 20,
        'exercise_minutes': [30] * 20
    })
    
    detected_anomalies = detect_anomalies(user_behavior_dataframe)
    
    # Filter detected anomalies targeting steps on the last day (2026-01-20)
    step_anomalies = [
        anomaly for anomaly in detected_anomalies 
        if anomaly['metric'] == 'steps' and anomaly['date'] == '2026-01-20'
    ]
    assert len(step_anomalies) == 1
    assert step_anomalies[0]['anomaly_type'] == 'low'
    assert "decline" in step_anomalies[0]['title'].lower() or "steps" in step_anomalies[0]['title'].lower()
    assert step_anomalies[0]['confidence'] >= 0.70

def test_detect_compound_digital_burnout():
    # 20 days of data: 19 stable, 1 day with screen time spike AND sleep duration drop
    dates = pd.date_range(start='2026-01-01', periods=20)
    screen_time_data = [4.0] * 19 + [9.5]  # Spike on day 20
    sleep_data = [7.5] * 19 + [4.0]       # Drop on day 20
    
    user_behavior_dataframe = pd.DataFrame({
        'user_id': ['U1'] * 20,
        'date': dates,
        'steps': [8000] * 20,
        'sleep_hours': sleep_data,
        'screen_time_hours': screen_time_data,
        'deep_work_hours': [3.0] * 20,
        'exercise_minutes': [30] * 20
    })
    
    detected_anomalies = detect_anomalies(user_behavior_dataframe)
    
    # Check for compound "Digital Burnout" anomaly on day 20
    compound_burnout_anomalies = [
        anomaly for anomaly in detected_anomalies 
        if anomaly['metric'] == 'compound_digital_burnout' and anomaly['date'] == '2026-01-20'
    ]
    assert len(compound_burnout_anomalies) == 1
    assert "burnout" in compound_burnout_anomalies[0]['title'].lower()
    assert compound_burnout_anomalies[0]['confidence'] >= 0.75
