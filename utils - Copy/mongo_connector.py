from pymongo import MongoClient
import pandas as pd


def connect_mongodb(uri="mongodb://localhost:27017/"):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.server_info()
        return client
    except Exception as e:
        raise Exception(f"MongoDB Connection Error: {e}")


def get_mongo_databases(client):
    return client.list_database_names()


def get_mongo_collections(client, db_name):
    db = client[db_name]
    return db.list_collection_names()


def load_collection_as_dataframe(client, db_name, collection_name, limit=1000):
    db = client[db_name]
    collection = db[collection_name]

    data = list(collection.find().limit(limit))

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    if "_id" in df.columns:
        df["_id"] = df["_id"].astype(str)

    return df