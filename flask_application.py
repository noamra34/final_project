from flask import Flask, request, jsonify, render_template, redirect, session
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from pymongo import MongoClient 
import bcrypt
import datetime

app = Flask(__name__)
MONGO_URI = "mongodb://super:noam123456789@mongodb:27017/supermarket"
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

# @app.route('/submit', methods=['POST'])
# @jwt_required()
# def submit():
#     current_user_id = get_jwt_identity()
#     selected_product_ids = request.form.getlist('selected_products')
    
#     # Retrieve user document from MongoDB
#     user = db.users.find_one({'_id': ObjectId(current_user_id)})
    
#     if not user:
#         return jsonify({'msg': 'User not found'}), 404
    
#     selected_products = []
#     total_price = 0.0
    
#     # Fetch details of selected products from MongoDB
#     for product_id in selected_product_ids:
#         product = db.products.find_one({'_id': ObjectId(product_id)})
#         if product:
#             selected_products.append({
#                 'product_name': product.get('product_name'),
#                 'price': product.get('price'),
#                 'category': product.get('category')
#             })
#             total_price += float(product.get('price', 0.0))
    
#     # Update selected_products field in user document
#     db.users.update_one({'_id': ObjectId(current_user_id)}, {'$set': {'selected_products': selected_products}})
    
#     return render_template('submit.html', selected_products=selected_products, total_price=total_price)



    
if __name__ == '__main__':
    app.run(debug=True)

