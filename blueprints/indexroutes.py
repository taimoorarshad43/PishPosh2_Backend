from flask import Blueprint, session, render_template, request
from models import Product

indexroutes = Blueprint("indexroutes", __name__)


@indexroutes.route('/')
def home_page():

    offset = request.args.get('page', None)                      # We'll set the offset based on whether user selects 'next' or 'previous'
    pagination = session.get('page', 0)

    # Offset will either be "next" or "previous", we'll then increase pagination and use that in our SQLA query
    if not offset:                                           
        session['page'] = 0
        pagination = 0
    elif offset == 'next':
        pagination = session.get('page', 0)
        pagination += 1
        session['page'] = pagination
    else:
        pagination = session.get('page', 0)
        pagination -= 1
        session['page'] = pagination


    if pagination < 1:  # To prevent negative pages
        pagination = 0
        session['page'] = pagination

    pagination = pagination* 20

    products = Product.query.offset(pagination).limit(20).all() # Get a bunch of products to display on the homepage. TODO: Randomize order of products listed

    return render_template('index.html', products = products)

@indexroutes.app_errorhandler(404)                      # Uses .app_errorhandler because regular error handlers only latch onto blueprints and not entire app
def page_not_found(e):
    print(e)
    return render_template('404.html'), 404

