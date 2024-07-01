from flask import Flask, request, jsonify, render_template, redirect, session
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from pymongo import MongoClient 
import bcrypt
import datetime

app = Flask(__name__)
MONGO_URI = "mongodb://super:noam123456789@localhost:27017/supermarket"
client = MongoClient(MONGO_URI)
db = client.supermarket
jwt = JWTManager(app)

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/profile')
# def profile():
#     username = session.get('username')
#     if username:
#         # Query user data from the database based on user_id
#         user = db.users.find_one({'username': username})
#         if user:
#             return render_template('hello.html', user=user)
#     return redirect('/')

@app.route('/invalid')
def invalid():
    return render_template('invalide.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        selected_products = []
        if (not (username and password and email)) and selected_products is None:
            return render_template('signup.html', message="all fields are required")
        hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        db.users.insert_one({'username': username, 'password': hashed_password, 'email': email})
        
        return redirect('/')
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.users.find_one({'username': username})
        if user is not None:
            if bcrypt.checkpw(password.encode('utf-8'), user['password']):
                print("connected successfully")
                return redirect('/')
            else:
                return redirect('/invalid')
        return redirect('/signup')
    return render_template('/login.html')

@app.route('/products', methods=['GET'])
def products():
    products_cursor = db.products.find({}, {"product_name": 1,'price': 1,"category": 1, "_id": 0})  # Fetch only product_name field
    products_list = [product for product in products_cursor]
    print("Fetched products:", products_list)
    return render_template('/products.html', products=products_list)

@app.route('/submit', methods=['POST'])
@jwt_required()
def submit():
    current_user_id = get_jwt_identity()
    selected_product_ids = request.form.getlist('selected_products')
    
    # Retrieve user document from MongoDB
    user = db.users.find_one({'_id': ObjectId(current_user_id)})
    
    if not user:
        return jsonify({'msg': 'User not found'}), 404
    
    selected_products = []
    total_price = 0.0
    
    # Fetch details of selected products from MongoDB
    for product_id in selected_product_ids:
        product = db.products.find_one({'_id': ObjectId(product_id)})
        if product:
            selected_products.append({
                'product_name': product.get('product_name'),
                'price': product.get('price'),
                'category': product.get('category')
            })
            total_price += float(product.get('price', 0.0))
    
    # Update selected_products field in user document
    db.users.update_one({'_id': ObjectId(current_user_id)}, {'$set': {'selected_products': selected_products}})
    
    return render_template('submit.html', selected_products=selected_products, total_price=total_price)



    
if __name__ == '__main__':
    app.run(debug=True)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/signup', methods=['POST', 'GET'])
# def signup():
#     if request.method == 'POST':
#         data = request.form
#         username = data.get('username')
#         password = data.get('password')
#         email = data.get('email')
#         phone = data.get('phone')
#         hashed_password = generate_password_hash(password)
#         mongo.db.users.insert_one({
#             'username': username, 
#             'password': hashed_password, 
#             'email': email, 
#             'phone': phone
#         })
#         return jsonify({'msg': 'User created successfully'}), 201
#     return render_template('signup.html')


# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         data = request.form
#         username = data.get('username')
#         password = data.get('password')
#         user = mongo.db.users.find_one({'username': username})
#         if user and check_password_hash(user['password'], password):
#             access_token = create_access_token(identity=str(user['_id']))
#             return redirect(url_for('home'))
#         return jsonify({'msg': 'Bad username or password'}), 401
#     return render_template('login.html')
    

# @app.route('/products', methods=['POST'])
# @jwt_required()
# def add_product():
#     data = request.json
#     product = {
#         'name': data.get('name'),
#         'description': data.get('description'),
#         'price': data.get('price'),
#         'quantity': data.get('quantity'),
#         'created_at': datetime.datetime.utcnow()
#     }
#     mongo.db.products.insert_one(product)
#     return jsonify({'msg':'Product added successfully'}), 201


# # @app.route('/products', methods=['GET'])
# # def get_products():
# #     products = list(mongo.db.products.find())
# #     for product in products:
# #         product['_id'] = str(product['_id'])
# #     return jsonify(products), 200
# @app.route('/products', methods=['GET'])
# def get_products():
#     try:
#         products = list(mongo.db.supermarket.products.find())
#         for product in products:
#             product['_id'] = str(product['_id'])
#         return jsonify(products), 200
#     except Exception as e:
#         print(f"An error occurred: {e}")
        

# @app.route('/products/<product_id>', methods=['PUT'])
# @jwt_required
# def update_product(product_id):
#     data = request.json
#     mongo.db.products.update_one(
#         {'_id': ObjectId(product_id)},
#         {'$set': data}
#     )
#     return jsonify({'msg': 'Product updated successfully'}), 200

# @app.route('/products/<product_id>', methods=['DELETE'])
# @jwt_required()
# def delete_product(product_id):
#     mongo.db.products.delete_one({'_id': ObjectId(product_id)})
#     return jsonify({'msg': 'Product deleted successfully'})

# @app.route('/cart', methods=['POST'])
# @jwt_required()
# def add_to_cart():
#     data = request.json
#     current_user = get_jwt_identity()
#     cart_item = {
#         'product_id': data.get('product_id'),
#         'quantity': data.get('quantity'),
#         'user_id': current_user,
#         'added_at': datetime.datetime.utcnow()
#     }
#     mongo.db.cart.insert_one(cart_item)
#     return jsonify({'msg': 'Item added to cart successfully'}), 201

# @app.route('/cart', methods=['GET'])
# @jwt_required()
# def get_cart():
#     current_user = get_jwt_identity()
#     cart_items = list(mongo.db.cart.find({'user_id': current_user}))
#     for item in cart_items:
#         item['_id'] = str(item['_id'])
#     return jsonify(cart_items), 200

# @app.route('/cart/<cart_item_id>', methods=['PUT'])
# @jwt_required()
# def update_cart_item(cart_item_id):
#     data = request.json
#     current_user = get_jwt_identity()
#     mongo.db.cart.update_one(
#         {'_id': ObjectId(cart_item_id), 'user_id': current_user},
#         {'$set': data}
#     )
#     return jsonify({'msg': 'Cart item updated successfully'}), 200

# @app.route('/cart/<cart_item_id>', methods=['DELETE'])
# @jwt_required()
# def delete_cart_item(cart_item_id):
#     current_user = get_jwt_identity()
#     mongo.db.cart.delete_one({'_id': ObjectId(cart_item_id), 'user_id': current_user})
#     return jsonify({'msg': 'Cart item deleted successfully'}), 200

# @app.route('/orders', methods=['POST'])
# @jwt_required()
# def place_order():
#     current_user = get_jwt_identity()
#     cart_items = list(mongo.db.cart.find({'user_id': current_user}))
#     order = {
#         'user_id': current_user,
#         'items': cart_items,
#         'total': sum(item['quantity'] * mongo.db.products.find_one({'_id': ObjectId(item['product_id'])})['price'] for item in cart_items),
#         'ordered_at': datetime.datetime.utcnow()
#     }
#     mongo.db.orders.insert_one(order)
#     mongo.db.cart.delete_many({'user_id': current_user})
#     return jsonify({'msg': 'Order placed successfully'}), 201

# @app.route('/orders', methods=['GET'])
# @jwt_required()
# def get_orders():
#     current_user = get_jwt_identity()
#     orders = list(mongo.db.orders.find({'user_id': current_user}))
#     for order in orders:
#         order['_id'] = str(order['_id'])
#     return jsonify(orders), 200

# if __name__ == '__main__':
#     app.run(debug=True)
