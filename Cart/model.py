import pymongo
import config

try:
    client = pymongo.MongoClient(config.DB_CONNECTION_STR)
    db = client[config.DATABASE]
    coll_cart = db['cart']
    coll_order = db['orders']
except Exception as e:
    print('Unable to connect to database')



def insert_item(item):
    # Check if item already in cart, in that case update its quantity
    if coll_cart.count_documents({'userId':item['userId'],'itemId':item['itemId']}) > 0:
        result = coll_cart.update_one({'userId':item['userId'],'itemId':item['itemId']},{'quantity':{'$inc':item['quantity']}})
    else:
        result = coll_cart.insert_one(item)
    
    return result


def get_items_from_cart(userId):
    return coll_cart.find({'userId':userId},projection={'_id':False})
    
def remove_item(item):
    result = coll_cart.delete_many(item)
    return result.deleted_count


def getMaxOrderId():
    order = coll_order.find_one(sort=[('orderId',pymongo.DESCENDING)])
    if order:
        return order['orderId']+1
    else:
        return 1

def add_order(item):
    result = coll_order.insert_one(item)
    return result.inserted_id