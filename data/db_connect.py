import os

import pymongo as pm

LOCAL = "0"
CLOUD = "1"

SE_DB = 'seDB'

client = None

MONGO_ID = '_id'


def connect_db():
    """
    Provides a uniform way to connect to the DB across all uses.
    Returns a MongoClient object or sets the global client variable.
    """
    global client
    if client is None:  # If not already connected
        print("Setting client because it is None.")
        if os.environ.get("CLOUD_MONGO", "LOCAL") == "CLOUD":
            # Check environment variable
            password = os.environ.get("GAME_MONGO_PW")
            print('PASSWORD: ', password)

            password = 'mongoPASSWORD'  # temporary put it here for TA to use

            if not password:
                raise ValueError("You must set your password to \
                                use Mongo in the cloud.")
            print("Connecting to Mongo in the cloud.")
            # Use your MongoDB Atlas connection string
            uri = f"mongodb+srv://yw5954:{password}@cluster0.q7jza.mongodb.net\
                /?retryWrites=true&w=majority&appName=Cluster0"
            # Use ServerApi for MongoDB Atlas
            client = pm.MongoClient(uri,
                                    server_api=pm.server_api.ServerApi('1'))
            # Test the connection with a ping
            try:
                client.admin.command('ping')
                print("Pinged your deployment. \
                Successfully connected to MongoDB!")
            except Exception as e:
                raise ConnectionError(f"Failed to connect to MongoDB: {e}")
        else:
            print("Connecting to Mongo locally.")
            client = pm.MongoClient()  # Connect to the local MongoDB instance
    return client


def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        # Convert mongo ID to a string so it works as JSON
        doc[MONGO_ID] = str(doc[MONGO_ID])


def create(collection, doc, db=SE_DB):
    """
    Insert a single doc into collection.
    """
    print(f'{db=}')
    return client[db][collection].insert_one(doc)


def insert_one(collection, doc, db=SE_DB):
    """
    Insert a single doc into collection.
    """
    print(f'{db=}')
    return client[db][collection].insert_one(doc)


def read_one(collection, filt, db=SE_DB):
    """
    Find with a filter and return on the first doc found.
    Return None if not found.
    """
    for doc in client[db][collection].find(filt):
        convert_mongo_id(doc)
        return doc


def del_one(collection, filt, db=SE_DB):
    """
    Find with a filter and return on the first doc found.
    """
    del_result = client[db][collection].delete_one(filt)
    return del_result.deleted_count


def update_doc(collection, filters, update_dict, db=SE_DB):
    return client[db][collection].update_one(filters, {'$set': update_dict})


def fetch_all(collection, db=SE_DB):
    ret = []
    for doc in client[db][collection].find():
        ret.append(doc)
    return ret


def read(collection, db=SE_DB, no_id=True) -> list:
    """
    Returns a list from the db.
    """
    ret = []
    for doc in client[db][collection].find():
        if no_id:
            del doc[MONGO_ID]
        else:
            convert_mongo_id(doc)
        ret.append(doc)
    return ret


def read_dict(collection, key, db=SE_DB, no_id=True) -> dict:
    recs = read(collection, db=db, no_id=no_id)
    recs_as_dict = {}
    for rec in recs:
        recs_as_dict[rec[key]] = rec
    return recs_as_dict


def fetch_all_as_dict(key, collection, db=SE_DB):
    ret = {}
    for doc in client[db][collection].find():
        del doc[MONGO_ID]
        ret[doc[key]] = doc
    return ret
