import pandas as pd
import streamlit as st
from pymongo import MongoClient, UpdateOne
import certifi

# Try to get the URI from Streamlit secrets, or default to localhost for local dev if not set
try:
    # Adding ?retryWrites=true&w=majority for Atlas stability
    MONGO_URI = st.secrets["MONGO_URI"]
except FileNotFoundError:
    # Fallback for local testing if secrets.toml is missing (User should configure this)
    MONGO_URI = "mongodb://localhost:27017/" 
except KeyError:
     MONGO_URI = "mongodb://localhost:27017/"

DB_NAME = "data_pipeline"

def get_db():
    """Connect to MongoDB and return the database object."""
    # ca=certifi.where() is often needed for SSL handshake on some networks/clouds
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    return client[DB_NAME]

def init_db():
    """
    Initialize MongoDB collections with indexes.
    MongoDB creates databases/collections on first write, but indexes should be explicit.
    """
    db = get_db()
    
    # Create unique indexes to prevent duplicates (acting like Primary Keys)
    try:
        db.scraped_books.create_index("title", unique=True)
        db.scraped_quotes.create_index("text", unique=True)
        # Compound index for jobs
        db.scraped_jobs.create_index([("title", 1), ("company", 1), ("location", 1)], unique=True)
        print("MongoDB Indexes initialized.")
    except Exception as e:
        print(f"Index initialization warning: {e}")

def save_data(df, collection_name):
    """
    Save a pandas DataFrame to the specified MongoDB collection, avoiding duplicates via Upsert.
    """
    if df.empty:
        print(f"No data to save to {collection_name}")
        return

    db = get_db()
    collection = db[collection_name]
    
    # Convert DataFrame to list of dicts
    records = df.to_dict("records")
    
    operations = []
    
    for record in records:
        # Define unique query based on collection
        if collection_name == 'scraped_books':
            query = {"title": record['title']}
        elif collection_name == 'scraped_quotes':
            query = {"text": record['text']}
        elif collection_name == 'scraped_jobs':
            query = {
                "title": record['title'],
                "company": record['company'],
                "location": record['location']
            }
        else:
            # Fallback for unknown tables (just insert, no check?) 
            # Better to default to something safe or skip
            continue
            
        # Add scrape timestamp if not present (handled by DB default in SQL, explicit here)
        if 'scraped_at' not in record:
            from datetime import datetime
            record['scraped_at'] = datetime.utcnow()
            
        # UpdateOne with upsert=True replaces existing or inserts new
        operations.append(UpdateOne(query, {"$set": record}, upsert=True))
        
    if operations:
        try:
            result = collection.bulk_write(operations)
            print(f"Synced {collection_name}: {result.upserted_count} new, {result.modified_count} updated.")
        except Exception as e:
            print(f"Error saving to {collection_name}: {e}")

def load_data(collection_name):
    """Load data from a MongoDB collection into a pandas DataFrame."""
    db = get_db()
    try:
        data = list(db[collection_name].find({}, {'_id': 0})) # Exclude MongoDB's internal _id
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error loading {collection_name}: {e}")
        return pd.DataFrame()

def query_data(collection_name, query, projection=None, limit=0):
    """
    Query data from MongoDB with a specific filter.
    Returns a pandas DataFrame.
    """
    db = get_db()
    try:
        # Exclude _id by default if projection is not provided, or merge it
        if projection:
            if "_id" not in projection:
                projection["_id"] = 0
        else:
            projection = {"_id": 0}
            
        cursor = db[collection_name].find(query, projection)
        
        if limit > 0:
            cursor = cursor.limit(limit)
            
        data = list(cursor)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error querying {collection_name}: {e}")
        return pd.DataFrame()


def clear_data(collection_name):
    """Clear all documents from a specific collection."""
    db = get_db()
    try:
        db[collection_name].delete_many({})
        print(f"Cleared {collection_name}")
    except Exception as e:
        print(f"Error clearing {collection_name}: {e}")
