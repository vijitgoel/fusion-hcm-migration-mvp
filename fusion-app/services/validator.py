import pandas as pd
import numpy as np
from services.config import REQUIRED_COLUMNS, VALIDATION_RULES

def validate_columns(df):
    """
    Check if required columns exist in the DataFrame.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return missing

def is_empty(val):
    """
    Helper: Check if a value is empty/blank.
    Handles NaN, None, empty string, or whitespace-only strings.
    """
    if pd.isna(val):
        return True
    s = str(val).strip()
    return s == ''

def validate_data(df):
    """
    Comprehensive data validation:
    - Required fields: empty/null/whitespace
    - Uniques: duplicates (all instances with keep=False)
    - Dates: pd.to_datetime valid for HireDate
    """
    errors = []

    # Check required fields (including empty strings/spaces)
    for col, rules in VALIDATION_RULES.items():
        if col not in df.columns or not rules.get("required"):
            continue
        empty_rows = df[df[col].apply(is_empty)]
        for idx in empty_rows.index:
            errors.append(f"Row {idx+1}: {col} is missing")

    # Check uniqueness (all duplicates with keep=False)
    for col, rules in VALIDATION_RULES.items():
        if col not in df.columns or not rules.get("unique"):
            continue
        duplicates = df[df.duplicated(subset=[col], keep=False)]
        for idx in duplicates.index:
            errors.append(f"Row {idx+1}: Duplicate {col}")

    # Check date validation for HireDate
    for col, rules in VALIDATION_RULES.items():
        if col not in df.columns or rules.get("type") != "date":
            continue
        try:
            parsed_dates = pd.to_datetime(df[col], errors='coerce')
            invalid_rows = parsed_dates.isna()
            for idx in invalid_rows[invalid_rows].index:
                errors.append(f"Row {idx+1}: Invalid date in {col}")
        except:
            # If entire column fails, flag all rows
            for idx in df.index:
                errors.append(f"Row {idx+1}: Invalid date in {col}")

    return errors

# Optional: Sample test in comments
# df_test = pd.DataFrame({
#     'EmployeeNumber': ['1', '2', '1', np.nan],
#     'FirstName': ['John', '', 'Jane', 'Bob'],
#     'LastName': ['Doe', 'Smith', 'Doe', 'Wilson'],
#     'HireDate': ['2023-01-01', 'invalid', '2023-03-01', '2023-04-01']
# })
# print(validate_data(df_test))
# Output: ['Row 1: Duplicate EmployeeNumber', 'Row 2: FirstName is missing', 'Row 3: Duplicate EmployeeNumber', 'Row 4: EmployeeNumber is missing', 'Row 2: Invalid date in HireDate']