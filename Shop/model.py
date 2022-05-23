import pymongo
import config

try:
    client = pymongo.MongoClient(config.DB_CONNECTION_STR)
    db = client[config.DATABASE]
    coll_inventory = db['Inventory']
except Exception as e:
    print('Unable to connect to database')


def add_items(items):               # list of documents to insert
    if items:
        result = coll_inventory.insert_many(items)
    return result.inserted_ids

def update_item(find,update):
    result = coll_inventory.update_one(find,update)
    return result.modified_count

def remove_item(item):
    result = coll_inventory.delete_many(item)
    return result.deleted_count

def get_items(find,projection=None,sort=None):
    if sort and '-' in sort:
        sort = (sort.split('-')[0],pymongo.DESCENDING)
    result = coll_inventory.find(find, projection=projection).sort(sort)
    return result

def itemExists(itemName):
    return coll_inventory.count_documents({'name':itemName}) > 0