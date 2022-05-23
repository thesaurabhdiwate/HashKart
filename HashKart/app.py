from flask import Flask, request, jsonify
import requests
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from datetime import datetime,timedelta
import config
import model as db
import logging



app = Flask(__name__)
log = app.logger
log.setLevel(logging.INFO)

def token_required(func):
    @wraps(func)
    def validate_token(*args, **kwargs):
        token = None
        # Check token in header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            log.error('Token missing!')
            return jsonify({'message' : 'Token is missing!'}), 401

        # Decode token and check validity
        try:
            data = jwt.decode(token, config.SECRET_KEY)
            current_user = data['userId']
        except:
            log.error('Token is invalid! Please login again')
            return jsonify({'message' : 'Token is invalid! Please login again'}), 401

        return func(current_user = current_user, *args, **kwargs)

    return validate_token


@app.route('/addUser', methods=['POST'])
def addUser():
    try:
        # get user data
        userData = request.get_json()
        
        # validate
        if not userData:
            return jsonify({'message': 'Invalid data!'}), 401
        if {'userId','password','userName'} - set(userData):
            return jsonify({'message' : 'Mandatory Parameters missing!'}), 401
        if db.user_exists(userData['userId']):
            return jsonify({'message' : 'User already exists!'}), 401
        
        # encode password
        userData['password'] = generate_password_hash(userData['password'],method='sha256')

        # Add record
        db.insert_user(userData)
        return jsonify({'message':'user created!!'})
    
    except Exception as e:
        print(e)
        log.error('unable to create user!')
        return jsonify({'message' : 'unable to create user!'}), 401


@app.route('/login', methods=['POST'])
def login():
    # Get data
    userCred = request.get_json()

    # Validate
    if 'userId' not in userCred or 'password' not in userCred:
        log.error('Mandatory Parameters missing!')
        return jsonify({'message' : 'Mandatory Parameters missing!'}), 401
    user = db.get_user({'userId':userCred['userId']})
    if not user:
        log.error('User does not exist!')
        return jsonify({'message' : 'User does not exist!'}), 401
    if check_password_hash(user['password'], userCred['password']):
        # Valid, now return new token
        token = jwt.encode({'userId' : user['userId'], 'exp' : datetime.utcnow() + timedelta(minutes=config.SESSION_TIME)}, config.SECRET_KEY)
        return jsonify({'authToken' : token.decode('UTF-8')})
    else:
        log.error('Invalid Credentials')
        return jsonify({'message' : 'Invalid Credentials'}), 401

@app.route('/addInventory',methods=['POST'])
def addInventory():
    # Get Data
    Item = request.get_json()
    #redirect to shop services
    response = requests.post(config.SHOP_SERVICE_URL+'addInventory',json=Item)
    return response.json()


@app.route('/showInventory',methods=['GET'])
@token_required
def getInventory(current_user):
    response = requests.get(config.SHOP_SERVICE_URL+'getInventory',params=request.args.to_dict())
    return jsonify(response.json())


@app.route('/addToCart', methods=['POST'])
@token_required
def addToCart(current_user):
    try:
        # Get data
        item = request.get_json()

        # check if quantity is present in Inventory
        response = requests.get(config.SHOP_SERVICE_URL+'itemAvailable',params=item)

        if not response.json()['available']:
            return jsonify({'message': 'Requested quantity not available'}), 401

        item['userId'] = current_user
        response = requests.post(config.CART_SERVICE_URL+'addToCart',json=item)
        return response.json()
    except Exception as e:
        print(e)
        log.error('Unable to add item to cart')
        return jsonify({'message':'Unable to add item to cart'}), 401

@app.route('/removeFromCart', methods=['POST'])
@token_required
def removeFromCart(current_user):
    try:
        # Get data
        item = request.get_json()
        item['userId'] = current_user
        response = requests.post(config.CART_SERVICE_URL+'removeFromCart',json=item)
        return response.json()
    except Exception as e:
        print(e)
        log.error('Unable remove cart items')
        return jsonify({'message':'Unable remove cart items'}), 401



@app.route('/getCart', methods=['GET'])
@token_required
def getCart(current_user):
    try:
        #Get cart items for user
        userData = {'userId':current_user}
        response = requests.get(config.CART_SERVICE_URL+'getCart',params=userData)
        return jsonify(response.json())
    except Exception as e:
        print(e)
        log.error('Unable get cart items')
        return jsonify({'message':'Unable get cart items'}), 401

@app.route('/checkout', methods=['POST'])
@token_required
def checkout(current_user):
    try:
        # Get data
        data = {}
        #Get cart items for user
        userData = {'userId':current_user}
        response = requests.get(config.CART_SERVICE_URL+'getCart',params=userData)
        cartData = response.json()
        
        data['TOTAL'] = cartData[-1]['TOTAL']
        cartData = cartData[:-1]            # Removing total

        # check if quantity is present in Inventory
        for item in cartData:
            available = requests.get(config.SHOP_SERVICE_URL+'itemAvailable',params={'itemId':item['itemId'], 'quantity':item['quantity']})
            if not available.json()['available']:
                return jsonify({'message': 'Requested quantity not available'}), 401

        data['cartItems'] = cartData
        result = requests.post(config.CART_SERVICE_URL+'checkout',json=data)

        if result.json()['message'] == 'Success':
            # Now reduce items
            for item in cartData:
                result = requests.post(config.SHOP_SERVICE_URL+'reduceInventory',json={'itemId':item['itemId'], 'quantity':(-1*item['quantity'])})

            #clear the cart
            requests.post(config.CART_SERVICE_URL+'removeFromCart',json={'userId':current_user})

        return jsonify({'message':'Order Placed Successfully!'})

    except Exception as e:
        print(e)
        log.error('Unable to checkout')
        return jsonify({'message':'Unable to checkout'}), 401


if __name__ == '__main__':
    app.run(port=5000,debug=True)