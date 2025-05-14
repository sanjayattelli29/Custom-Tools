import pymongo
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'qr_database')

# Global MongoDB client and database instances
client = None
db = None

def connect_to_mongodb():
    """Connect to MongoDB and return the database instance"""
    global client, db
    try:
        if not client:
            client = pymongo.MongoClient(MONGODB_URI)
            db = client[DB_NAME]
            print(f"Connected to MongoDB: {DB_NAME}")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return None

def get_collection(collection_name):
    """Get a MongoDB collection by name"""
    try:
        database = connect_to_mongodb()
        if database:
            return database[collection_name]
        return None
    except Exception as e:
        print(f"Error getting collection {collection_name}: {str(e)}")
        return None

def insert_document(collection_name, document):
    """Insert a document into a collection"""
    try:
        collection = get_collection(collection_name)
        if collection:
            result = collection.insert_one(document)
            return result.inserted_id
        return None
    except Exception as e:
        print(f"Error inserting document: {str(e)}")
        return None

def find_document(collection_name, query):
    """Find a document in a collection"""
    try:
        collection = get_collection(collection_name)
        if collection:
            return collection.find_one(query)
        return None
    except Exception as e:
        print(f"Error finding document: {str(e)}")
        return None

def find_documents(collection_name, query=None, sort=None, limit=0):
    """Find multiple documents in a collection"""
    try:
        collection = get_collection(collection_name)
        if collection:
            cursor = collection.find(query or {})
            
            if sort:
                cursor = cursor.sort(sort[0], sort[1])
            
            if limit > 0:
                cursor = cursor.limit(limit)
            
            return list(cursor)
        return []
    except Exception as e:
        print(f"Error finding documents: {str(e)}")
        return []

def update_document(collection_name, query, update, upsert=False):
    """Update a document in a collection"""
    try:
        collection = get_collection(collection_name)
        if collection:
            result = collection.update_one(query, {'$set': update}, upsert=upsert)
            return result.modified_count
        return 0
    except Exception as e:
        print(f"Error updating document: {str(e)}")
        return 0

def delete_document(collection_name, query):
    """Delete a document from a collection"""
    try:
        collection = get_collection(collection_name)
        if collection:
            result = collection.delete_one(query)
            return result.deleted_count
        return 0
    except Exception as e:
        print(f"Error deleting document: {str(e)}")
        return 0