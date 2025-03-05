import os
import requests
from bson.objectid import ObjectId

import pymongo as pm

LOCAL = "LOCAL"
CLOUD = "CLOUD"

JOURNAL_DB = 'journalDB'
DB = JOURNAL_DB

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
        if os.environ.get("CLOUD_MONGO", LOCAL) == CLOUD:
            # Check environment variable
            password = os.environ.get("MONGO_PW")
            print('PASSWORD: ', password)

            password = 'mongoPASSWORD'  # temporary put it here for TA to use

            if not password:
                raise ValueError("You must set MONGO_PW to your password \
                                to use Mongo in the cloud.")
            print("Connecting to Mongo in the cloud.")
            # Use your MongoDB Atlas connection string
            uri = (
                f"mongodb+srv://yw5954:{password}@cluster0.q7jza.mongodb.net/"
                "?retryWrites=true&w=majority&appName=Cluster0"
            )
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


def create(collection, doc, db=JOURNAL_DB):
    """
    Insert a single doc into collection.
    """
    print(f'{db=}')
    return client[db][collection].insert_one(doc)


def read_one(collection, filt, db=JOURNAL_DB):
    """
    Find with a filter and return on the first doc found.
    Return None if not found.
    """
    for doc in client[db][collection].find(filt):
        convert_mongo_id(doc)
        return doc


def delete(collection, mongo_id):
    """
    Delete from mongo collection.

    Args:
        collection: collection name
        mongo_id: can be a string ID, ObjectId, or dict with ID inside

    Returns:
        The ID of the deleted document if successful, None otherwise
    """
    try:
        if not mongo_id:
            raise ValueError('No ID specified for deletion')

        # 如果mongo_id是字典并且包含_id键
        if isinstance(mongo_id, dict) and '_id' in mongo_id:
            # 将ObjectId对象转换为字符串以便比较
            if isinstance(mongo_id['_id'], ObjectId):
                result_id = str(mongo_id['_id'])
                client[DB][collection].delete_one({'_id': mongo_id['_id']})
                return result_id
            else:
                # 如果不是ObjectId，尝试原样删除
                client[DB][collection].delete_one(mongo_id)
                return str(mongo_id['_id']) if mongo_id['_id'] else None

        # 如果mongo_id是字符串ID
        elif isinstance(mongo_id, str) and id_is_valid(mongo_id):
            client[DB][collection].delete_one({'_id': ObjectId(mongo_id)})
            return mongo_id

        # 如果mongo_id是ObjectId
        elif isinstance(mongo_id, ObjectId):
            client[DB][collection].delete_one({'_id': mongo_id})
            return str(mongo_id)

        # 如果是其他字典，尝试按条件删除
        elif isinstance(mongo_id, dict):
            result = client[DB][collection].delete_one(mongo_id)
            if result.deleted_count > 0:
                return str(result.deleted_count)
            else:
                return None

        return None
    except Exception as e:
        print(f"Error in delete: {str(e)}")
        return None


def delete_doc(collection, field, value):
    """
    Delete from mongo collection based on matching field/value pair.
    """
    client[DB][collection].delete_one({field: value})
    return value


def delete_many(collection, field, value):
    """
    Delete from mongo collection based on matching field/value pair.

    Args:
        collection: collection name
        field: field name to match
        value: value to match against

    Returns:
        The DeleteResult object from pymongo
    """
    result = client[DB][collection].delete_many({field: value})
    return result


def update(collection, filters, update_dict, db=JOURNAL_DB):
    """
    Update a document in the database.
    collection: the name of the collection
    filters: dictionary of key-value pairs for filtering documents
    update_dict: dictionary of key-value pairs to be updated
    db: the database to use
    returns: The result of the update operation
    """
    if not update_dict:
        raise ValueError("Update dictionary cannot be empty")

    result = client[db][collection].update_one(
        filters,
        {'$set': update_dict}
    )
    return result.modified_count


def update_doc(collection, filters, update_data):
    """
    Update a document in MongoDB.
    collection: the MongoDB collection to update
    filters: a dictionary of filters to find the document to update
    update_data: a dictionary of fields and values to update
    returns: the number of modified documents
    """
    result = client[DB][collection].update_one(
        filters,
        {'$set': update_data}
    )
    return result.modified_count


def update_typed_doc(collection, key_name, key_val, filters, update_data):
    """
    Update a document in MongoDB with ID conversion if needed.
    collection: the MongoDB collection to update
    key_name: the name of the primary key field
    key_val: the value of the primary key
    filters: additional filters to find the document
    update_data: a dictionary of fields and values to update
    """
    if key_name == '_id' and not isinstance(key_val, ObjectId):
        if ObjectId.is_valid(key_val):
            key_val = ObjectId(key_val)
        else:
            raise ValueError(f"Invalid ObjectId format: {key_val}")

    combined_filters = {key_name: key_val}
    combined_filters.update(filters)

    result = client[DB][collection].update_one(
        combined_filters,
        {'$set': update_data}
    )
    return result.modified_count


def read(collection, db=JOURNAL_DB, no_id=True) -> list:
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


def read_dict(collection, key, db=JOURNAL_DB, no_id=True) -> dict:
    recs = read(collection, db=db, no_id=no_id)
    recs_as_dict = {}
    for rec in recs:
        recs_as_dict[rec[key]] = rec
    return recs_as_dict


def fetch_all_as_dict(key, collection, db=JOURNAL_DB):
    ret = {}
    for doc in client[db][collection].find():
        del doc[MONGO_ID]
        ret[doc[key]] = doc
    return ret


def read_many(collection, filt, db=JOURNAL_DB, no_id=False) -> list:
    """
    Find many documents with a filter and return a list of them.

    Args:
        collection: The collection to read from
        filt: The filter to apply
        db: The database to use
        no_id: If True, remove the MongoDB _id field

    Returns:
        A list of dict objects with the documents matching the filter
    """
    ret = []
    for doc in client[db][collection].find(filt):
        if no_id:
            if MONGO_ID in doc:
                del doc[MONGO_ID]
        ret.append(doc)
    return ret


def get_json(endpoint):
    """
    Get JSON from endpoint.
    endpoint: URL to fetch from
    returns: dict representation of JSON returned from endpoint
    """
    response = requests.get(endpoint)
    return response.json()


def id_is_valid(mongo_id):
    """
    Check if a MongoDB ID is valid.
    """
    return ObjectId.is_valid(mongo_id)
