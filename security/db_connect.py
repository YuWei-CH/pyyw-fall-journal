import os
import pymongo as pm

LOCAL = "LOCAL"
CLOUD = "CLOUD"

SECURITY_DB = 'securityDB'  # Separate database for security data
SECURITY_COLLECTION = 'security'

client = None
MONGO_ID = '_id'


def connect_db():
    """
    Provides a uniform way to connect to the database.
    Returns a MongoClient object or sets the global client variable.
    """
    global client
    if client is None:  # If not already connected
        print("Setting client because it is None.")
        if os.environ.get("CLOUD_MONGO", LOCAL) == CLOUD:
            password = os.environ.get("MONGO_PW", "mongoPASSWORD")
            uri = (
                f"mongodb+srv://yw5954:{password}@cluster0.q7jza.mongodb.net/"
                "?retryWrites=true&w=majority&appName=Cluster0"
            )
            client = pm.MongoClient(uri,
                                    server_api=pm.server_api.ServerApi('1'))
            try:
                client.admin.command('ping')
                print("Successfully connected to MongoDB!")
            except Exception as e:
                raise ConnectionError(f"Failed to connect to MongoDB: {e}")
        else:
            print("Connecting to Mongo locally.")
            client = pm.MongoClient()  # Local MongoDB connection
    return client


def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        # Convert mongo ID to a string so it works as JSON
        doc[MONGO_ID] = str(doc[MONGO_ID])


def create(collection, doc, db=SECURITY_DB):
    """
    Inserts a single document into a MongoDB collection.
    """
    return connect_db()[db][collection].insert_one(doc)


def read_one(collection, filt, db=SECURITY_DB):
    """
    Finds a single document in a collection that matches a filter.
    Returns `None` if not found.
    """
    doc = connect_db()[db][collection].find_one(filt)
    if doc:
        convert_mongo_id(doc)
    return doc


def delete(collection, filt, db=SECURITY_DB):
    """
    Deletes a document from a collection that matches a filter.
    Returns the number of deleted documents (0 or 1).
    """
    del_result = connect_db()[db][collection].delete_one(filt)
    return del_result.deleted_count


def update(collection, filters, update_dict, db=SECURITY_DB):
    """
    Updates a document in a collection using a filter.
    Uses `$set` to update only specific fields.
    """
    return connect_db()[db][collection].update_one(
        filters, {'$set': update_dict})
