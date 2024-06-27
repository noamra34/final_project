from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/supermarket"
app.config["JWT_SECRET_KEY"] = "noamguy0309"
mongo = PyMongo(app)
jwt = JWTManager(app)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    hashed_password = generate_password_hash(password)
    mongo.db.users._insert_one({'username': username, 'password':hashed_password})
    return jsonify({'msg':'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get('username')
    username = data.get('username')
    password = data.get('password')
    user = mongo.db.users.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify(access_token=access_token)
    return jsonify({'msg':'Bad username or password'}), 401

@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    data = request.json
    product = {
        'name': data.get('name'),
        'description': data.get('description'),
        'price': data.get('price'),
        'quantity': data.get('quantity'),
        'created_at': datetime.datetime.utcnow()
    }
    mongo.db.products.insert_one(product)
    return jsonify({'msg':'Product added successfully'}), 201


@app.route('/products', methods=['GET'])
def get_products():
    products = list(mongo.db.products.find())
    for product in products:
        product['_id'] = str(product['_id'])
    return jsonify(products), 200

@app.route('/products/<product_id>', methods=['PUT'])
@jwt_required
def update_product(product_id):
    data = request.json
    mongo.db.products.update_one(
        {'_id': ObjectId(product_id)},
        {'$set': data}
    )
    return jsonify({'msg': 'Product update successfully'}), 200

@app.route('/products/<product_id>', methods=['DELETE'])
@jwt_required
def delete_product(product_id):
    mongo.db.products.delete_one({'_id': ObjectId(product_id)})
    return jsonify({'msg': 'Product delete successfully'})

@app.route('/cart', methods=['POST'])
@jwt_required
def add_to_cart():
    data = request.json
    current_user = get_jwt_identity()
    cart_item = {
        'product_id': data.get('product_id'),
        'quantity': data.get('quantity'),
        'user_id': current_user,
        'added_at': datetime.datetime.utcnow()
    }
    mongo.db.cart.insert_one(cart_item)
    return jsonify({'msg': 'Item added to cart succefully '}), 201

@app.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    current_user = get_jwt_identity()
    cart_items = list(mongo.db.cart.find({'user_id': current_user}))
    for item in cart_items:
        item['_id'] = str(item['_id'])
    return jsonify(cart_items), 200

@app.route('/cart/<cart_item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(cart_item_id):
    data = request.json
    current_user = get_jwt_identity()
    mongo.db.cart.update_one(
        {'_id': ObjectId(cart_item_id), 'user_id': current_user},
        {'$set': data}
    )
    return jsonify({'msg': 'Cart item update successfully'}), 200

@app.route('/cart/<cart_item_id>', methods=['DELETE'])
@jwt_required()
def delete_cart_item(cart_item_id):
    current_user = get_jwt_identity()
    mongo.db.cart.delete_one({'_id': ObjectId(cart_item_id), 'user_id': current_user})
    return jsonify({'msg': 'Cart item delete successfully'}), 200

@app.route('/orders', methods=['POST'])
@jwt_required()
def place_order():
    current_user = get_jwt_identity()
    cart_items = list(mongo.db.cart.find({'user_id': current_user}))
    order = {
        'user_id': current_user,
        'items': cart_items,
        'total': sum(item['quantity'] * mongo.db.products.find_one({'_id': ObjectId(item['product_id'])})['price'] for item in cart_items),
        'ordered_at': datetime.datetime.utcnow()
    }
    mongo.db.orders.insert_one(order)
    mongo.db.cart.delete_many({'user_id': current_user})
    return jsonify({'msg': 'Order placed successfully'}), 201

@app.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    current_user = get_jwt_identity()
    orders = list(mongo.db.orders.find({'user_id': current_user}))
    for order in orders:
        order['_id'] = str(order['_id'])
    return jsonify(orders), 200

if __name__ == '__maim__':
    app.run(debug=True)





