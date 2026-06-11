def generate_insights(
    discovered_patterns: list, 
    detected_anomalies: list, 
    confidence_threshold: float = 0.70
) -> dict:
    """
    Synthesizes discovered behavioral patterns and detected anomalies into user insights.
    Enforces Component 4 (Evidence Sufficiency) by filtering out insights below the confidence threshold.

    Args:
        discovered_patterns (list): Discovered trends and correlations.
        detected_anomalies (list): Detected daily statistical deviations.
        confidence_threshold (float): Minimum confidence level below which insights are withheld.

    Returns:
        dict: A dictionary mapping user_id to a list of sorted, high-confidence insights.
    """
    synthesized_user_insights = {}
    
    # 1. Process long-horizon patterns (Component 1 & 3)
    for pattern in discovered_patterns:
        user_id = pattern['user_id']
        confidence_score = pattern['confidence']
        
        # Component 4: Evidence Sufficiency Check
        if confidence_score < confidence_threshold:
            # Suppress/abstain from reporting low-confidence insights
            continue
            
        if user_id not in synthesized_user_insights:
            synthesized_user_insights[user_id] = []
            
        synthesized_user_insights[user_id].append({
            'type': 'pattern',
            'insight': pattern['title'],
            'confidence': round(confidence_score, 2),
            'evidence': pattern['evidence'],
            'metric': pattern['metric'],
            'date': None,
            'details': pattern['raw_details']
        })
        
    # 2. Process daily anomalies (Component 2 & 3)
    for anomaly in detected_anomalies:
        user_id = anomaly['user_id']
        confidence_score = anomaly['confidence']
        
        # Component 4: Evidence Sufficiency Check
        if confidence_score < confidence_threshold:
            # Suppress/abstain from reporting low-confidence insights
            continue
            
        if user_id not in synthesized_user_insights:
            synthesized_user_insights[user_id] = []
            
        synthesized_user_insights[user_id].append({
            'type': 'anomaly',
            'insight': f"Anomaly detected on {anomaly['date']}: {anomaly['title']}",
            'confidence': round(confidence_score, 2),
            'evidence': anomaly['explanation'],
            'metric': anomaly['metric'],
            'date': anomaly['date'],
            'details': anomaly['raw_details']
        })
        
    # Sort insights for each user: place trends first, sorted by confidence (highest first)
    for user_id in synthesized_user_insights:
        synthesized_user_insights[user_id] = sorted(
            synthesized_user_insights[user_id],
            key=lambda insight_item: (insight_item['type'] == 'anomaly', -insight_item['confidence'])
        )
        
    return synthesized_user_insights
