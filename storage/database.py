import pandas as pd
import streamlit as st
import sqlite3
import os
from datetime import datetime

# Path to the SQLite database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data_pipeline.db")
DB_NAME = "SQLite (data_pipeline.db)"

def get_db():
    """Connect to SQLite and return the connection object."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_resource
def init_db():
    """
    Initialize SQLite database tables with appropriate schemas.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraped_books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT UNIQUE,
                    price REAL,
                    rating TEXT,
                    availability TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraped_quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT UNIQUE,
                    author TEXT,
                    tags TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraped_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    date_posted TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(title, company, location)
                )
            """)
            conn.commit()
        print("SQLite Database initialized.")
    except Exception as e:
        print(f"Database initialization warning: {e}")

def save_data(df, collection_name):
    """
    Save a pandas DataFrame to the specified SQLite table, avoiding duplicates via INSERT OR REPLACE.
    """
    if df.empty:
        print(f"No data to save to {collection_name}")
        return

    # Add scraped_at if missing
    df = df.copy()
    if 'scraped_at' not in df.columns:
        df['scraped_at'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    else:
        df['scraped_at'] = df['scraped_at'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if hasattr(x, 'strftime') else str(x)
        )

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Fetch target table schema to filter columns
            cursor.execute(f"PRAGMA table_info({collection_name})")
            table_cols = {row[1] for row in cursor.fetchall()}
            
            # Filter DataFrame columns to only match schema (excluding autoincrement ID)
            columns = [c for c in df.columns if c in table_cols and c != 'id']
            if not columns:
                print(f"No matching columns to save to {collection_name}")
                return

            placeholders = ", ".join(["?"] * len(columns))
            col_names = ", ".join(columns)
            
            query = f"INSERT OR REPLACE INTO {collection_name} ({col_names}) VALUES ({placeholders})"
            
            records = [tuple(x) for x in df[columns].to_numpy()]
            
            cursor.executemany(query, records)
            conn.commit()
            print(f"Synced {collection_name}: {cursor.rowcount} rows inserted/replaced.")
    except Exception as e:
        print(f"Error saving to {collection_name}: {e}")

@st.cache_data(ttl=60)
def load_data(collection_name):
    """Load data from a SQLite table into a pandas DataFrame."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Check if table exists
            cursor = conn.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{collection_name}'")
            if not cursor.fetchone():
                return pd.DataFrame()

            df = pd.read_sql_query(f"SELECT * FROM {collection_name}", conn)
            
            if 'id' in df.columns:
                df = df.drop(columns=['id'])
                
            # If quotes, convert tags comma-separated string back to list of strings
            if collection_name == 'scraped_quotes' and 'tags' in df.columns:
                df['tags'] = df['tags'].apply(
                    lambda x: [t.strip() for t in x.split(',')] if isinstance(x, str) and x else []
                )
                
            return df
    except Exception as e:
        print(f"Error loading {collection_name}: {e}")
        return pd.DataFrame()

def query_data(collection_name, query, projection=None, limit=0):
    """
    Query data from SQLite with a specific filter.
    Returns a pandas DataFrame.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Check if table exists
            cursor = conn.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{collection_name}'")
            if not cursor.fetchone():
                return pd.DataFrame()

            where_clauses = []
            params = []
            
            for key, val in query.items():
                if isinstance(val, dict):
                    # Handle MongoDB operators
                    for op, op_val in val.items():
                        if op == "$regex":
                            where_clauses.append(f"{key} LIKE ?")
                            params.append(f"%{op_val}%")
                        elif op == "$options":
                            pass
                        elif op == "$gte":
                            where_clauses.append(f"{key} >= ?")
                            params.append(op_val)
                        elif op == "$lte":
                            where_clauses.append(f"{key} <= ?")
                            params.append(op_val)
                        elif op == "$gt":
                            where_clauses.append(f"{key} > ?")
                            params.append(op_val)
                        elif op == "$lt":
                            where_clauses.append(f"{key} < ?")
                            params.append(op_val)
                else:
                    if key == "tags":
                        where_clauses.append(f"{key} LIKE ?")
                        params.append(f"%{val}%")
                    else:
                        where_clauses.append(f"{key} = ?")
                        params.append(val)

            where_sql = ""
            if where_clauses:
                where_sql = " WHERE " + " AND ".join(where_clauses)

            limit_sql = ""
            if limit > 0:
                limit_sql = f" LIMIT {limit}"

            sql_query = f"SELECT * FROM {collection_name}{where_sql}{limit_sql}"
            
            df = pd.read_sql_query(sql_query, conn, params=params)
            
            if 'id' in df.columns:
                df = df.drop(columns=['id'])
                
            if collection_name == 'scraped_quotes' and 'tags' in df.columns:
                df['tags'] = df['tags'].apply(
                    lambda x: [t.strip() for t in x.split(',')] if isinstance(x, str) and x else []
                )

            return df
    except Exception as e:
        print(f"Error querying {collection_name}: {e}")
        return pd.DataFrame()

def clear_data(collection_name):
    """Clear all documents from a specific collection."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {collection_name}")
            conn.commit()
            print(f"Cleared {collection_name}")
    except Exception as e:
        print(f"Error clearing {collection_name}: {e}")

