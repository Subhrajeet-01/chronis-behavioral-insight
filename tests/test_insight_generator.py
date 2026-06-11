import pytest
from engine.insight_generator import generate_insights

def test_generate_insights_threshold_filtering():
    # Mock patterns: one strong (0.85 confidence), one weak (0.62 confidence)
    mock_discovered_patterns = [
        {
            'user_id': 'U1',
            'metric': 'steps',
            'pattern_type': 'trend_decline',
            'title': 'Physical activity declined.',
            'evidence': 'Average steps decreased.',
            'confidence': 0.85,
            'raw_details': {}
        },
        {
            'user_id': 'U1',
            'metric': 'sleep_hours',
            'pattern_type': 'trend_incline',
            'title': 'Sleep increased.',
            'evidence': 'Sleep hours increased.',
            'confidence': 0.62,
            'raw_details': {}
        }
    ]
    
    # Mock anomalies: one strong (0.75 confidence), one weak (0.65 confidence)
    mock_detected_anomalies = [
        {
            'user_id': 'U1',
            'date': '2026-01-20',
            'metric': 'screen_time_hours',
            'anomaly_type': 'high',
            'title': 'Screen time spike.',
            'explanation': 'Screen time high.',
            'confidence': 0.75,
            'raw_details': {}
        },
        {
            'user_id': 'U1',
            'date': '2026-01-21',
            'metric': 'steps',
            'anomaly_type': 'low',
            'title': 'Steps low.',
            'explanation': 'Steps low today.',
            'confidence': 0.65,
            'raw_details': {}
        }
    ]
    
    # Run with default confidence threshold of 0.70 (evidence sufficiency filter)
    generated_user_insights = generate_insights(
        mock_discovered_patterns, 
        mock_detected_anomalies, 
        confidence_threshold=0.70
    )
    
    assert 'U1' in generated_user_insights
    user_one_insights = generated_user_insights['U1']
    
    # Only U1's 0.85 confidence pattern and 0.75 confidence anomaly should pass the filter
    assert len(user_one_insights) == 2
    
    filtered_insight_titles = [insight['insight'] for insight in user_one_insights]
    
    # Check that the high-confidence pattern is present
    assert 'Physical activity declined.' in filtered_insight_titles
    # Check that the high-confidence anomaly is present (will be prefixed with date)
    assert 'Anomaly detected on 2026-01-20: Screen time spike.' in filtered_insight_titles
    
    # Verify that weak insights below the 0.70 threshold are correctly withheld
    assert 'Sleep increased.' not in filtered_insight_titles
    assert any("2026-01-21" in title for title in filtered_insight_titles) is False
