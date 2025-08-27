from flask import Blueprint, session, render_template, jsonify
from models import Product, db
from sqlalchemy import inspect

productroutes = Blueprint("productroutes", __name__)

########################################################### Product Routes #####################################################################

@productroutes.route('/product/<int:productid>')
def getproduct(productid):

    product = Product.query.get_or_404(productid)

    # to bookmark what product we last visited, so we can redirect back to it
    session['lastviewedproduct'] = productid

    return render_template('productdetail.html', product=product)

@productroutes.route('/product/<int:productid>/related', methods = ['POST'])
def getrelatedproducts(productid):
    """
    Get related products based on the product ID.
    """
    # Check if the product exists first
    product = Product.query.get(productid)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    productlimit = 4

    # Get related products
    related_products = Product.query.filter(Product.tags.any(Product.tags.any(Product.productid != productid))).limit(productlimit).all()

    for product in related_products:
        product.image = product.decode_image()

    params = ['productid', 'productname', 'productdescription', 'price', 'user_id', 'image']
    serialized_related_products = [serialize(product, params) for product in related_products]

    # print("Related Products are", serialized_related_products)

    return jsonify(RelatedProducts=serialized_related_products), 200

@productroutes.route('/product/<int:productid>/delete', methods = ['DELETE'])
def deleteproduct(productid):

    product = Product.query.get(productid)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    try:
        db.session.delete(product)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Error deleting product:", e)
        return jsonify({'status': 'error', 'message': 'Failed to delete product.'}), 500

    return jsonify({'status': 'success', 'message': 'Product deleted successfully.'}), 200


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

################################################################################################################################################