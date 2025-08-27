from flask import Blueprint, jsonify
from flask_cors import cross_origin
from models import User, Product
from sqlalchemy import inspect


apiroutes = Blueprint("apiroutes", __name__)

@apiroutes.route('/users')
def getusers():

    # get all users
    sqlausers = User.query.all()

    params = ['id', 'username', 'firstname', 'lastname']

    users = [serialize(sqlauser, params) for sqlauser in sqlausers]

    return jsonify(Users=users)

@apiroutes.route('/users/<userid>')
def getsingleuser(userid):

    user = User.query.get(userid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    params = ['id', 'username', 'firstname', 'lastname']
    user = serialize(user, params)

    return jsonify(User=user)

@apiroutes.route('/users/<userid>/products')
def getsingleuserproducts(userid):

    user = User.query.get(userid)
    if not user:
        return jsonify({"error": "User not found"}), 404

    userproducts = []

    for product in user.products: # Get all user products to list on page
        product.image = product.decode_image()
        userproducts.append(product)

    params = ['id', 'username', 'firstname', 'lastname']
    user = serialize(user, params)

    products = [serialize(product, ['productid', 'productname', 'productdescription', 'price', 'user_id', 'image']) for product in userproducts]
    user['products'] = products

    return jsonify(User=user)

@apiroutes.route('/products')
def getproducts():

    sqlaproducts = Product.query.all()
    params = ['productid', 'productname', 'productdescription', 'price', 'user_id']
    products = [serialize(product, params) for product in sqlaproducts]

    return jsonify(Products=products)

@apiroutes.route('/products/<productid>')
@cross_origin(supports_credentials=True)
def getsingleproduct(productid):

    product = Product.query.get(productid)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    params = ['productid', 'productname', 'productdescription', 'price', 'user_id']
    product = serialize(product, params)

    return jsonify(Product=product)

@apiroutes.route('/productimages')
@cross_origin(supports_credentials=True)
def getproductsimages():

    """
    Route to get all products with their images decoded
    """

    sqlaproducts = Product.query.all()
    for product in sqlaproducts:
        product.image = product.decode_image()
    params = ['productid', 'productname', 'productdescription', 'price', 'user_id', 'image']
    products = [serialize(product, params) for product in sqlaproducts]

    return jsonify(Products=products)

@apiroutes.route('/productsimages/<productid>')
@cross_origin(supports_credentials=True)
def getsingleproductimages(productid):

    """
    Route to get a single product with its image decoded
    """

    product = Product.query.get(productid)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    username = product.user.username
    product.username = username
    product.image = product.decode_image()
    params = ['productid', 'productname', 'productdescription', 'price', 'image', 'user_id', 'user.username']

    mapper = inspect(product)
    output = {}

    for column in mapper.attrs:
        if column.key in params:
            output[column.key] = getattr(product, column.key)
    
    output['username'] = username
    product = output

    return jsonify(Product=product)


def serialize(object, params): # Helper function for serializing different SQLA objects

    """
    Serializer helper function. All it needs is the object and its respective params to serialize.

    Takes the object to be serialized as well as the params to serialize it with
    """

    # TODO: Refactor to allow SQLA relationships

    mapper = inspect(object)
    output = {}

    for column in mapper.attrs:
        if column.key in params:
            output[column.key] = getattr(object, column.key)

    return output


