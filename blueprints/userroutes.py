from flask import Blueprint, session, render_template, redirect, flash, request, jsonify, make_response, current_app
from flask_cors import cross_origin
from models import User, db
from forms import SignUpForm, ProductUploadForm
from sqlalchemy.exc import IntegrityError

userroutes = Blueprint("userroutes", __name__)

############################################################### User Routes ###############################################################

@userroutes.route('/user/<int:userid>')
def profile(userid):

    user = User.query.get_or_404(userid)

    userproducts = []

    for product in user.products: # Get all user products to list on page
        userproducts.append(product)

    return render_template('profile.html', user = user, products = userproducts)

@userroutes.route('/userdetail')
def userdetail():

    userid = session.get('userid', None)

    productform = ProductUploadForm()

    if userid:

        user = User.query.get_or_404(session.get('userid', -1))     # Should only be able to get here if you are logged in
        userproducts = []

        for product in user.products: # Get all user products to list on page
            userproducts.append(product)

        # Adding errors from the '/upload/userid' route to this form after a redirect
        # We need to validate the form object to do this
        productform.validate()
        productform.image.errors.append(session.pop("ProductFileError", ""))
        productform.name.errors.append(session.pop("ProductNameError", ""))
        productform.description.errors.append(session.pop("ProductDescriptionError", ""))
        productform.price.errors.append(session.pop("ProductPriceError", ""))

        return render_template('userdetail.html', user = user, products = userproducts, form = productform)
    
    else:

        flash('Please login to view your profile', 'btn-info')
        return redirect('/')
    
 
@userroutes.route('/signup', methods = ['POST'])
def signup():

    """
    Will add a new user with username and hashed password.

    If username is taken or there are issues with the inputted field, will return an array of errors
    and no user.
    """

    data = request.get_json()
    username = data['username']
    password = data['password']
    firstname = data['firstname']
    lastname = data['lastname']

    # Blank array of errors to append to if there are any issues with the inputted fields
    errors = {
        "firstname": [],
        "lastname": [],
        "username": [],
        "password": []
    }

    ####################### Validation of user input #################################
    if len(username) < 4:
        errors['username'].append("Username must be at least 4 characters long")
    if len(password) <= 6:
        errors['password'].append("Password must be at least 6 characters long")
    if len(firstname) == 0:
        errors['firstname'].append("You need to add your first name")
    ##################################################################################

    if errors['username'] or errors['password'] or errors['firstname']: # If any of our errors are populated then return with errors and no user
        output = {
            "user": False,
            "errors": errors
        }
        return jsonify(output)

    user = User.hashpassword(username, password, firstname, lastname)

    db.session.add(user)
    try:                            # Handles the possibility that the username is already taken
        db.session.commit()
        payload = user.username
    except IntegrityError:
        errors['username'].append("Username already taken")
        payload = False

    output = {
        "user": payload,
        "errors": errors
    }

    return jsonify(output)
    

@userroutes.route('/login', methods = ['POST'])
@cross_origin(supports_credentials=True)
def login():

    """
    Gets a username and password from the form and authenticates.

    Returns a user if the user is authenticated, otherwise returns False.
    """
    data = request.get_json()
    username = data['username']
    password = data['password']

    # If we have a valid user, then we will return the user's username otherwise it will return False
    # We'll also add to session the userid
    user = User.authenticate(username, password)
    if(user):
        session.permanent = True
        session['userid'] = user.id
        session.modified = True
        user = user.username
        
        # Enhanced debugging
        print(f"Session after setting: {dict(session)}")
        print(f"Session ID cookie: {request.cookies.get('session')}")
        print(f"All cookies: {dict(request.cookies)}")
        print(f"Response cookies: {dict(request.cookies)}")
        
        # Check Flask's default session cookie name
        from flask import current_app
        print(f"SECRET_KEY: {current_app.config.get('SECRET_KEY')}")
        print(f"SESSION_COOKIE_NAME: {current_app.config.get('SESSION_COOKIE_NAME', 'session')}")
        
        # Check if session cookie exists with different names
        print(f"All request cookies: {[name for name in request.cookies.keys()]}")
        
        # Check if session is actually being stored
        print(f"Session object type: {type(session)}")
        print(f"Session object: {session}")
        
    else:
        return jsonify("null")
    
    print("From /login route", session['userid'])

    return jsonify(user)

    
@userroutes.route('/logout', methods = ['POST'])
@cross_origin(supports_credentials=True)
def logout():

    # When you log out, remove userid from session and clear cart from session

    session.pop('userid', None)
    session.pop('username', None)
    session.pop('userfirstname', None)
    session.pop('userlastname', None)
    session.pop('cart', None)

    # Trying to remove everything from session after logout

    session.clear()

    print("From /logout route", session.get('userid', None))

    resp = make_response(jsonify("Logged out"))
    cookie_name = current_app.config.get('SESSION_COOKIE_NAME', 'session')
    resp.set_cookie(cookie_name, '', expires=0)
    resp.headers['Cache-Control'] = 'no-store' # Doing this in an attempt to prevent race condition with logging in and logging out.

    return resp
    
@userroutes.route('/@me')
@cross_origin(supports_credentials=True)
def me():

    """
    A route for a React frontend to check if a user is logged in and get their user information.
    """

    userid = session.get('userid', None)

    print("From /@me route userid is: ", userid)

    if not userid:
        return jsonify({"user": "null"}), 401
    
    # Since we have a userid in session via logging in we dont need to check if the userid exists - that was already done
    user = User.query.filter_by(id=userid).first()
    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "firstname": user.firstname,
            "lastname": user.lastname
        }
    })

# TODO: Delete User route - need to test this

@userroutes.route('/user/<int:userid>/delete')
def deleteuser(userid):

    User.query.get(userid).delete()
    db.session.commit()

    # Should delete all products associated with user as well

    # Should remove userid from session as well.

    session.pop['username', None]

    return redirect('/')


################################################################################################################################################

@userroutes.route('/test-session')
def test_session():
    """Test if Flask sessions are working at all"""
    session['test'] = 'hello'
    session.modified = True
    
    print(f"Test session set: {dict(session)}")
    print(f"All cookies in test: {dict(request.cookies)}")
    
    return jsonify({
        'session_data': dict(session),
        'cookies': dict(request.cookies),
        'session_object': str(session)
    })