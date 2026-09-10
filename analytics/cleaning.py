import pandas as pd


def clean_data(file_path):

    # Read CSV
    df = pd.read_csv(file_path)

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Remove spaces from column names
    df.columns = df.columns.str.strip()

    # Fill missing values
    for col in df.columns:

        if pd.api.types.is_numeric_dtype(df[col]):

            df[col] = df[col].fillna(df[col].median())

        else:

            df[col] = df[col].fillna("Unknown")

    return df