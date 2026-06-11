import pandas as pd
import os

# Expected columns and their types for CSV validation
EXPECTED_COLUMNS_AND_TYPES = {
    'user_id': str,
    'date': str,
    'steps': (int, float),
    'sleep_hours': (int, float),
    'screen_time_hours': (int, float),
    'deep_work_hours': (int, float),
    'exercise_minutes': (int, float)
}

def load_and_validate_data(dataset_file_path: str) -> pd.DataFrame:
    """
    Loads daily behavioral observations from a CSV file and validates its structure.

    Args:
        dataset_file_path (str): The path to the CSV dataset file.

    Returns:
        pd.DataFrame: A cleaned and chronologically sorted DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist at the specified path.
        ValueError: If the CSV is malformed or missing required columns.
    """
    if not os.path.exists(dataset_file_path):
        raise FileNotFoundError(f"Dataset file not found at: {dataset_file_path}")
        
    try:
        behavioral_dataframe = pd.read_csv(dataset_file_path)
    except Exception as read_error:
        raise ValueError(f"Failed to read CSV file: {read_error}")
        
    # Verify presence of all expected columns
    missing_required_columns = [
        column for column in EXPECTED_COLUMNS_AND_TYPES 
        if column not in behavioral_dataframe.columns
    ]
    if missing_required_columns:
        raise ValueError(f"Missing required dataset columns: {missing_required_columns}")
        
    # Convert date column to datetime objects
    behavioral_dataframe['date'] = pd.to_datetime(behavioral_dataframe['date'])
    
    # Sort chronologically by user and date to ensure proper trend analysis
    behavioral_dataframe = (
        behavioral_dataframe
        .sort_values(by=['user_id', 'date'])
        .reset_index(drop=True)
    )
    
    # Check for missing values and fill using forward-fill / backward-fill
    if behavioral_dataframe.isnull().any().any():
        behavioral_dataframe = (
            behavioral_dataframe
            .groupby('user_id')
            .apply(lambda user_group: user_group.ffill().bfill())
            .reset_index(drop=True)
        )
        
    return behavioral_dataframe
