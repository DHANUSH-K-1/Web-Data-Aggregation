import pandas as pd
import re

def clean_currency(value):
    """
    Extracts numeric value from currency strings like 'Â£51.77'.
    Returns float or None.
    """
    if pd.isna(value):
        return 0.0
    value_str = str(value)
    cleaned = re.sub(r'[^\d.]', '', value_str)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def normalize_text(text):
    """
    Removes extra whitespace and newlines.
    """
    if pd.isna(text):
        return ""
    return str(text).strip()

def clean_books_df(df):
    """
    Apply specific cleaning rules to the Books DataFrame.
    """
    df_clean = df.copy()
    if 'price' in df_clean.columns:
        df_clean['price'] = df_clean['price'].apply(clean_currency)
    if 'title' in df_clean.columns:
        df_clean['title'] = df_clean['title'].apply(normalize_text)
    return df_clean

def clean_quotes_df(df):
    """
    Apply specific cleaning rules to the Quotes DataFrame.
    """
    df_clean = df.copy()
    if 'text' in df_clean.columns:
        df_clean['text'] = df_clean['text'].apply(normalize_text)
    if 'author' in df_clean.columns:
        df_clean['author'] = df_clean['author'].apply(normalize_text)
    return df_clean

def clean_jobs_df(df):
    """
    Apply specific cleaning rules to the Jobs DataFrame.
    """
    df_clean = df.copy()
    if 'title' in df_clean.columns:
        df_clean['title'] = df_clean['title'].apply(normalize_text)
    if 'company' in df_clean.columns:
        df_clean['company'] = df_clean['company'].apply(normalize_text)
    if 'location' in df_clean.columns:
        df_clean['location'] = df_clean['location'].apply(normalize_text)
    return df_clean
