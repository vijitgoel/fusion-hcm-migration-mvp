import pandas as pd
from io import BytesIO
from .utils import generate_id

def read_file(file_path):
    if file_path.endswith(".xlsx"):
        return pd.read_excel(file_path)
    else:
        return pd.read_csv(file_path)

def normalize(df):
    df.columns = df.columns.str.strip()
    df.columns = [c.replace(" ", "") for c in df.columns]
    return df

def validate(df, required_columns):
    errors = []

    for col in required_columns:
        if col not in df.columns:
            errors.append({
                "id": generate_id(),
                "message": f"Missing column {col}"
            })

    return errors