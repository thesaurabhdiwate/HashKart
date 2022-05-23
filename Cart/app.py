from flask import Flask, request, jsonify
import model as db

app = Flask(__name__)


@app.route('/addToCart', methods=['POST'])
def addToCart():
    try:
        # get data
        data = request.get_json()
        result = db.insert_item(data)
        return jsonify({'message':'Item added to cart!'})

    except Exception as e:
        print(e)
        return jsonify({'message':'unable to add Items to cart'}), 401

@app.route('/removeFromCart', methods=['POST'])
def removeFromCart():
    try:
        # get data
        data = request.get_json()
        result = db.remove_item(data)
        return jsonify({'message':'Item removed from cart!'})

    except Exception as e:
        print(e)
        return jsonify({'message':'unable to remove Items from cart'}), 401


@app.route('/getCart',methods=['GET'])
def getCart():
    #Get userId
    userId = request.args.get('userId')
    cartList = list(db.get_items_from_cart(userId))
    
    # calculate total
    total = 0
    for item in cartList:
        total += item['quantity']*item['price']
    cartList.append({'TOTAL':total})

    return jsonify(cartList)



@app.route('/checkout', methods=['POST'])
def checkout():

    #GEt Data
    data = request.get_json()

    #get orderID
    orderId = db.getMaxOrderId()
    #redirect to payment gateaway
    paymentMethod = {'status':'success','type':'netBanking'}

    #insert into order table
    order = {}
    order['orderId'] = orderId
    order['paymentDetails'] = paymentMethod
    order['cartDetails'] = data

    db.add_order(order)
    

    return jsonify({'message':'Success'})

if __name__ == '__main__':
    app.run(port=5002,debug=True)