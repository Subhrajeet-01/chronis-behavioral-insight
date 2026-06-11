import json
import os
import pandas as pd
from jinja2 import Template

def get_abstention_counts(
    discovered_patterns: list, 
    detected_anomalies: list, 
    confidence_threshold: float = 0.70
) -> dict:
    """
    Counts how many insights/claims were withheld (abstained) because their
    confidence score fell below the evidence sufficiency threshold.

    Args:
        discovered_patterns (list): List of discovered long-horizon trends.
        detected_anomalies (list): List of detected daily anomalies.
        confidence_threshold (float): Sufficiency confidence barrier.

    Returns:
        dict: A mapping of user_id to the number of suppressed claims.
    """
    withheld_counts = {}
    
    # Identify the full set of unique user profiles
    all_user_ids = set(
        [pattern['user_id'] for pattern in discovered_patterns] + 
        [anomaly['user_id'] for anomaly in detected_anomalies]
    )
    for user_id in all_user_ids:
        withheld_counts[user_id] = 0
        
    for pattern in discovered_patterns:
        if pattern['confidence'] < confidence_threshold:
            withheld_counts[pattern['user_id']] = withheld_counts.get(pattern['user_id'], 0) + 1
            
    for anomaly in detected_anomalies:
        if anomaly['confidence'] < confidence_threshold:
            withheld_counts[anomaly['user_id']] = withheld_counts.get(anomaly['user_id'], 0) + 1
            
    return withheld_counts

def output_cli_report(user_insights: dict, withheld_counts: dict):
    """
    Prints a beautiful, structured CLI summary of the generated insights.

    Args:
        user_insights (dict): High-confidence insights grouped by user.
        withheld_counts (dict): Number of withheld insights grouped by user.
    """
    print("\n" + "="*80)
    print(" CHRONIS // BEHAVIORAL INSIGHT ENGINE (CLI SUMMARY)")
    print("="*80)
    
    for user_id, insight_list in user_insights.items():
        print(f"\n▶ PROFILE: {user_id}")
        print("-" * 40)
        
        patterns = [item for item in insight_list if item['type'] == 'pattern']
        anomalies = [item for item in insight_list if item['type'] == 'anomaly']
        
        print(f"  Long-horizon Patterns ({len(patterns)} active):")
        for pattern in patterns:
            print(f"    • {pattern['insight']}")
            print(f"      [Confidence: {pattern['confidence']:.2f}] — Evidence: {pattern['evidence']}")
            
        print(f"\n  Detected Anomalies ({len(anomalies)} active):")
        if not anomalies:
            print("     • No significant daily anomalies detected.")
        for anomaly in anomalies:
            print(f"    • {anomaly['insight']}")
            print(f"      [Confidence: {anomaly['confidence']:.2f}] — Explanation: {anomaly['evidence']}")
            
        suppressed_insight_count = withheld_counts.get(user_id, 0)
        print(f"\n  [Sufficiency Shield] {suppressed_insight_count} weak claim(s) suppressed for this profile.")
        print("-" * 40)
        
    print("="*80)
    print("Report generated successfully.")
    print("="*80 + "\n")

def generate_reports(
    behavioral_dataframe: pd.DataFrame, 
    user_insights: dict, 
    discovered_patterns: list, 
    detected_anomalies: list, 
    project_base_directory: str
):
    """
    Saves JSON and HTML reports, and outputs a console summary.

    Args:
        behavioral_dataframe (pd.DataFrame): Dataset rows.
        user_insights (dict): Final generated insights.
        discovered_patterns (list): Discovered patterns before sufficiency filter.
        detected_anomalies (list): Detected anomalies before sufficiency filter.
        project_base_directory (str): The project's root folder path.
    """
    # 1. Calculate the number of abstentions (suppressed insights)
    withheld_counts = get_abstention_counts(discovered_patterns, detected_anomalies)
    
    # 2. Print console CLI report
    output_cli_report(user_insights, withheld_counts)
    
    # 3. Write JSON data export
    json_export_structure = {
        'insights': user_insights,
        'abstention_counts': withheld_counts
    }
    json_output_path = os.path.join(project_base_directory, 'chronis_report.json')
    with open(json_output_path, 'w') as json_file:
        json.dump(json_export_structure, json_file, indent=2)
    print(f"JSON report saved to: {json_output_path}")
    
    # 4. Generate visual HTML dashboard report
    formatted_dataframe = behavioral_dataframe.copy()
    formatted_dataframe['date'] = formatted_dataframe['date'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    serializable_data_records = formatted_dataframe.to_dict(orient='records')
    
    template_path = os.path.join(project_base_directory, 'engine', 'report_template.html')
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"HTML Dashboard Template not found at: {template_path}")
        
    with open(template_path, 'r') as template_file:
        template_raw_content = template_file.read()
        
    jinja_template = Template(template_raw_content)
    
    rendered_dashboard_content = jinja_template.render(
        data_json=json.dumps(serializable_data_records),
        insights_json=json.dumps(user_insights),
        abstention_counts_json=json.dumps(withheld_counts)
    )
    
    html_output_path = os.path.join(project_base_directory, 'chronis_report.html')
    with open(html_output_path, 'w') as html_file:
        html_file.write(rendered_dashboard_content)
    print(f"HTML dashboard saved to: {html_output_path}")
