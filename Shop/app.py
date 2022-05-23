from bson import ObjectId
from flask import Flask, request, jsonify
import model as db





app = Flask(__name__)


@app.route('/addInventory',methods=['POST'])
def addInventory():
    try:
        # Get data
        inventory = request.get_json()

        # Check if already present
        if db.itemExists(inventory['name']):
            # add to the lot
            quantity = inventory['quantity']
            updated = db.update_item({'name':inventory['name']},{'$inc':{'quantity':quantity}})
            if updated:
                return jsonify({'message':'Item added to Inventory'})
        else:
            #Add to Inventory
            count = db.add_items([inventory])
            if count:
                return jsonify({'message':'Item added to Inventory'})
    except Exception as e:
        print(e)
        return jsonify({'message':'unable to add the item'}), 401


@app.route('/getInventory',methods=['GET'])
def getInventory():
    try:
        sort = 'name'
        if request.args.get('sort'):
            sort = request.args.get('sort')
        # Get all available items
        retList = list(db.get_items({'quantity':{'$gt':0}},sort=sort))
        
        # changing object id to string
        for item in retList:
            item['_id'] = str(item['_id'])

        # Return them
        return jsonify(retList)

    except Exception as e:
        print(e)
        return jsonify({'message':'unable to fetch Items'}), 401
    

@app.route('/itemAvailable', methods=['GET'])
def checkItemAvailable():
    try:
        # get data
        if request.args.get('itemId'):
            itemId = request.args.get('itemId')

        if request.args.get('quantity'):
            reqQuantity = int(request.args.get('quantity'))

        item = list(db.get_items({'_id':ObjectId(itemId)},sort='name'))[0]

        if item['quantity'] >= reqQuantity:
            return jsonify({'available':True})
        else:
            return jsonify({'available':False})
    except Exception as e:
        print(e)
        return jsonify('error')

@app.route('/reduceInventory',methods=['POST'])
def reduceQuantity():
    # Get item
    inventory = request.get_json()
    quantity = inventory['quantity']
    updated = db.update_item({'_id':ObjectId(inventory['itemId'])},{'$inc':{'quantity':quantity}})
    if updated:
        return jsonify({'message':'Item Updated'})
    else:
        return jsonify({'message':'Unable to update item'})

if __name__ == '__main__':
    app.run(port=5001,debug=True)