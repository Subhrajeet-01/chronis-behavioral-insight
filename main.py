import argparse
import sys
import os
from engine import (
    load_and_validate_data,
    discover_patterns,
    detect_anomalies,
    generate_insights,
    generate_reports
)

def main():
    command_line_parser = argparse.ArgumentParser(
        description="Chronis Behavioral Insight Engine - Synthesizing daily observations into coherent stories."
    )
    command_line_parser.add_argument(
        '--data', 
        type=str, 
        default='Chronis_TaskA_Synthetic_Behavioral_Data_v2-2 (1).csv',
        help="Path to the synthetic behavioral observations CSV file."
    )
    command_line_parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=0.70,
        help="Minimum confidence threshold (Component 4) to output an insight."
    )
    
    parsed_arguments = command_line_parser.parse_args()
    
    # Resolve the directory structure relative to the execution script
    project_base_directory = os.path.dirname(os.path.abspath(__file__))
    dataset_file_path = os.path.join(project_base_directory, parsed_arguments.data)
    
    print(f"Starting Chronis Behavioral Insight Engine...")
    print(f"Using dataset: {dataset_file_path}")
    print(f"Sufficiency confidence threshold: {parsed_arguments.confidence_threshold}")
    
    try:
        # 1. Ingestion & Validation
        behavioral_dataframe = load_and_validate_data(dataset_file_path)
        unique_user_count = behavioral_dataframe['user_id'].nunique()
        print(f"Loaded {len(behavioral_dataframe)} observations for {unique_user_count} unique profiles.")
        
        # 2. Pattern Discovery
        discovered_patterns = discover_patterns(behavioral_dataframe)
        print(f"Discovered {len(discovered_patterns)} raw behavioral patterns/trends.")
        
        # 3. Anomaly Detection
        detected_anomalies = detect_anomalies(behavioral_dataframe)
        print(f"Detected {len(detected_anomalies)} raw daily anomalies.")
        
        # 4. Insight Generation & Sufficiency Filtering
        user_insights = generate_insights(
            discovered_patterns, 
            detected_anomalies, 
            confidence_threshold=parsed_arguments.confidence_threshold
        )
        total_valid_insights = sum(len(insight_list) for insight_list in user_insights.values())
        print(
            f"Evidence Sufficiency check completed: {total_valid_insights} insights "
            f"passed the {parsed_arguments.confidence_threshold} threshold."
        )
        
        # 5. Output Reports (CLI Summary, JSON structure, HTML dashboard)
        generate_reports(
            behavioral_dataframe, 
            user_insights, 
            discovered_patterns, 
            detected_anomalies, 
            project_base_directory
        )
        
    except Exception as execution_error:
        print(f"\n[Error] Pipeline execution failed: {execution_error}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
