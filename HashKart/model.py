import pymongo
import config

try:
    client = pymongo.MongoClient(config.DB_CONNECTION_STR)
    db = client[config.DATABASE]
    coll_user = db['User']
except Exception as e:
    print('Unable to connect to database')



def insert_user(user):
    user = coll_user.insert_one(user)
    if user.inserted_id:
        return coll_user.find_one({'_id':user.inserted_id})


def get_user(find):
    user = coll_user.find_one(find)
    return user

def user_exists(userId):
    return coll_user.count_documents({'userId':userId}) > 0