import pytest
import pandas as pd
import numpy as np
from engine.pattern_discovery import discover_patterns

def test_discover_declining_activity_trend():
    # Mock data: 23 days of high step counts (~10,000 steps), followed by 7 days of lower step counts (~5,000 steps)
    dates = pd.date_range(start='2026-01-01', periods=30)
    steps_data = (
        [10000 + np.random.randint(-500, 500) for _ in range(23)] + 
        [5000 + np.random.randint(-500, 500) for _ in range(7)]
    )
            
    user_behavior_dataframe = pd.DataFrame({
        'user_id': ['U1'] * 30,
        'date': dates,
        'steps': steps_data,
        'sleep_hours': [7.0] * 30,
        'screen_time_hours': [5.0] * 30,
        'deep_work_hours': [3.0] * 30,
        'exercise_minutes': [30] * 30
    })
    
    discovered_patterns = discover_patterns(user_behavior_dataframe)
    
    # Filter discovered patterns targeting step activity
    step_trend_patterns = [pattern for pattern in discovered_patterns if pattern['metric'] == 'steps']
    assert len(step_trend_patterns) == 1
    assert step_trend_patterns[0]['pattern_type'] == 'trend_decline'
    assert "declined" in step_trend_patterns[0]['title']
    assert step_trend_patterns[0]['confidence'] >= 0.70

def test_no_trend_on_stable_data():
    # Mock data with constant stable values (no trend should be discovered)
    dates = pd.date_range(start='2026-01-01', periods=30)
    user_behavior_dataframe = pd.DataFrame({
        'user_id': ['U1'] * 30,
        'date': dates,
        'steps': [8000] * 30,
        'sleep_hours': [7.0] * 30,
        'screen_time_hours': [5.0] * 30,
        'deep_work_hours': [3.0] * 30,
        'exercise_minutes': [30] * 30
    })
    
    discovered_patterns = discover_patterns(user_behavior_dataframe)
    
    # Filter trend patterns
    trend_patterns = [
        pattern for pattern in discovered_patterns 
        if pattern['pattern_type'] in ['trend_decline', 'trend_incline']
    ]
    assert len(trend_patterns) == 0

def test_screen_time_sleep_correlation():
    # Create a linear negative relationship: sleep = 10.0 - screen_time * 0.8
    dates = pd.date_range(start='2026-01-01', periods=30)
    screen_time_data = np.linspace(2.0, 8.0, 30)
    sleep_data = 10.0 - screen_time_data * 0.8  
    
    user_behavior_dataframe = pd.DataFrame({
        'user_id': ['U1'] * 30,
        'date': dates,
        'steps': [8000] * 30,
        'sleep_hours': sleep_data,
        'screen_time_hours': screen_time_data,
        'deep_work_hours': [3.0] * 30,
        'exercise_minutes': [30] * 30
    })
    
    discovered_patterns = discover_patterns(user_behavior_dataframe)
    
    correlation_patterns = [
        pattern for pattern in discovered_patterns 
        if pattern['metric'] == 'screen_time_vs_sleep'
    ]
    assert len(correlation_patterns) == 1
    assert correlation_patterns[0]['pattern_type'] == 'correlation'
    assert correlation_patterns[0]['confidence'] > 0.80
