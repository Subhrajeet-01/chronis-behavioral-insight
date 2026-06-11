import pytest
import pandas as pd
import os
from engine.parser import load_and_validate_data

def test_load_and_validate_valid(tmp_path):
    # Create a valid test CSV file in the temporary path
    temp_csv_file = tmp_path / "valid_observations.csv"
    csv_raw_data = (
        "user_id,date,steps,sleep_hours,screen_time_hours,deep_work_hours,exercise_minutes\n"
        "U1,2026-01-01,8000,7.5,4.0,2.5,30\n"
        "U1,2026-01-02,9000,7.0,5.0,3.0,40\n"
    )
    temp_csv_file.write_text(csv_raw_data)
    
    parsed_dataframe = load_and_validate_data(str(temp_csv_file))
    assert len(parsed_dataframe) == 2
    assert list(parsed_dataframe.columns) == [
        'user_id', 'date', 'steps', 'sleep_hours', 'screen_time_hours', 'deep_work_hours', 'exercise_minutes'
    ]
    assert parsed_dataframe['steps'].iloc[0] == 8000
    assert pd.api.types.is_datetime64_any_dtype(parsed_dataframe['date'])

def test_load_and_validate_missing_columns(tmp_path):
    temp_csv_file = tmp_path / "invalid_observations.csv"
    # Missing steps column in the data
    csv_raw_data = (
        "user_id,date,sleep_hours,screen_time_hours,deep_work_hours,exercise_minutes\n"
        "U1,2026-01-01,7.5,4.0,2.5,30\n"
    )
    temp_csv_file.write_text(csv_raw_data)
    
    with pytest.raises(ValueError) as exception_info:
        load_and_validate_data(str(temp_csv_file))
    assert "Missing required dataset columns" in str(exception_info.value)

def test_load_and_validate_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_and_validate_data("non_existent_behavioral_data.csv")
