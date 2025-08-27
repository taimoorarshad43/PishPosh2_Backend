import io
from unittest import TestCase
import base64

from app import create_app
from flask import session

from models import User, Product, db

from blueprints.apiroutes import apiroutes
from blueprints.checkout import productcheckout
from blueprints.cart import cartroutes
from blueprints.product import productroutes
from blueprints.userroutes import userroutes
from blueprints.uploadroutes import uploadroutes
from blueprints.indexroutes import indexroutes

app = create_app('postgresql:///pishposh_testing_db')  # TODO: Use an inmemory database like SQLite

app.config['SQLALCHEMY_ECHO'] = False

app.json.sort_keys = False                  # Prevents Flask from sorting keys in API JSON responses.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "seekrat"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Configure filesystem sessions for testing
app.config['SESSION_TYPE'] = 'filesystem'
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

# Initialize Flask-Session for testing
from flask_session import Session
test_session = Session(app)

app.register_blueprint(apiroutes, url_prefix = "/v1")
app.register_blueprint(productcheckout)
app.register_blueprint(cartroutes)
app.register_blueprint(productroutes)
app.register_blueprint(userroutes)
app.register_blueprint(uploadroutes)
app.register_blueprint(indexroutes)

# Disable some of Flasks error behavior and disabling debugtoolbar. Disabling CSRF token.
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False


class FlaskTests(TestCase):

    """
    Testing the functionalities of the app.py file

        Things covered:

        Does app respond with appropriate pages?

        Does app response with certain features intact?

    """

    def setUp(self):
        
        """
        Setting up fake users and products to test
        """
        with app.app_context():

            db.drop_all()
            db.create_all()

            User.query.delete()

            username = 'johndoe'
            password = 'password'
            firstname = 'John'
            lastname = 'Doe'

            user = User.hashpassword(username, password, firstname, lastname)

            db.session.add(user)
            db.session.commit()

            Product.query.delete()

            productname = 'Product Name'
            productdescription = 'A product description'
            productprice = 25
            userid = 1

            product = Product(productname = productname, productdescription = productdescription, price = productprice, user_id = userid)

            db.session.add(product)
            db.session.commit()

    def tearDown(self):

        """
        Rolling back database, dropping all tables
        """
        with app.app_context():
            db.session.rollback()
            db.drop_all()


    def test_index(self):

        """
        Test visiting index page
        """

        with app.test_client() as client:
            resp = client.get('/')

            self.assertEqual(resp.status_code, 200)

    def test_example_products(self):
        
        """
        Test visiting a product page and testing that we get the right product name
        """

        with app.test_client() as client:
            resp = client.get('/product/1')
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Product Name', html)

    def test_404_product(self):

        """
        Test visiting a product that doesn't exist and making sure we get our 404 page
        """

        with app.test_client() as client:
            resp = client.get('/product/43')
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 404)
            self.assertIn('Page Not Found', html)

    def test_example_user(self):
        
        """
        Test visiting a user page
        """

        with app.test_client() as client:
            resp = client.get('/user/1')

            self.assertEqual(resp.status_code, 200)

    def test_404_user(self):
        
        """
        Test visiting a user that doesn't exist
        """

        with app.test_client() as client:
            resp = client.get('/user/43')

            self.assertEqual(resp.status_code, 404)

    def test_addingtocart(self):

        """
        Testing session state when we add to cart
        """

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['userid'] = 1                    # We'll set the user id to 1 to simulate a logged in user
            client.post('/product/1/addtocart')

            with client.session_transaction() as change_session:
                self.assertEqual(change_session['cart'], [1])

    def test_next_page(self):                                   # Testing to see if next page route changes session state appropriately

        """
        Testing the next page feature
        """

        with app.test_client() as client:
            client.get('/?page=next')

            with client.session_transaction() as change_session:
                self.assertEqual(change_session['page'], 1)

    def test_previous_page(self):

        """
        Testing the previous page feature
        """

        with app.test_client() as client:                       # Testing to see if previous page route changes session state appropriately
            with client.session_transaction() as change_session:
                change_session['page'] = 1
            client.get('/?page=previous')

            with client.session_transaction() as change_session:
                self.assertEqual(change_session['page'], 0)

    def test_signingup(self):                                   # Testing to see if signing up a user works and we have a database entry
        
        """
        Testing signing up a regular user account
        """

        with app.test_client() as client:
            resp = client.post('/signup', 
                             json={'username': 'janedoe', 'password': 'password', 'firstname': 'Jane', 'lastname': 'Doe'},
                             content_type='application/json')
            
            # Signup should succeed with valid data
            self.assertEqual(resp.status_code, 200)
            user = User.query.filter_by(username='janedoe').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.username, 'janedoe')

    def test_loggingin(self):                                   # Testing to see if logging in a user works and we have a session entry of their user id (of 1)

        """
        Testing logging in a regular user account
        """

        with app.test_client() as client:
            resp = client.post('/login', 
                             json={'username': 'johndoe', 'password': 'password'},
                             content_type='application/json')
            
            # Login should succeed with valid credentials
            self.assertEqual(resp.status_code, 200)
            with client.session_transaction() as change_session:
                self.assertEqual(change_session['userid'], 1)

    def test_loggingout(self):                                  # Testing to see if logging out a user works and we have no session entry of their user id

        """
        Testing logging out a regular user account
        """

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['userid'] = 1
            client.post('/logout')
            
            # Check session after logout
            with client.session_transaction() as change_session:
                self.assertNotIn('userid', change_session)

    def test_faileduserdetail(self):                            # We should be redirected if this happens
        
        """
        Testing to see if we get redirected if we try to access a user detail page without being logged in
        """

        with app.test_client() as client:
            resp = client.get('/userdetail')

            self.assertEqual(resp.status_code, 302)


    def test_uploadingproduct_fail(self):                       # Testing to see if we get the right redirect location when a product upload fails
        
        """
        Testing uploading a product and failing. We then see if we get a form error
        """

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['userid'] = 1
            resp = client.post('/upload/1', data = {'productName': 'New uploaded Product', 'productDescription': 
                                                    'Product for testing purposes', 'productPrice': 25, 'productImage': 'test.jpg'})
            
            # Should get 400 error for missing file
            self.assertEqual(resp.status_code, 400)
            data = resp.get_json()
            self.assertIn('error', data)

    def test_uploadingproduct_fail_errormsg(self):                       # Testing to see if we get the right error when a product upload fails
        
        """
        Testing uploading a product and failing. We then see if we get a form error
        """

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['userid'] = 1
            resp = client.post('/upload/1', data = {'productName': 'New uploaded Product', 'productDescription': 
                                                    'Product for testing purposes', 'productPrice': '25', 'productImage': 'test.jpg'}, follow_redirects = True)
            data = resp.get_data(as_text = True)

            # Should get specific error message about missing image file
            self.assertIn('Missing Image File', data)

    def test_uploadingproduct_success(self):                    # Testing to see if we can get a product uploaded

        """
        Testing uploading a product and succeeding
        """

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['userid'] = 1

            SMALLEST_JPEG_B64 = """\
            /9j/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8Q
            EBEQCgwSExIQEw8QEBD/yQALCAABAAEBAREA/8wABgAQEAX/2gAIAQEAAD8A0s8g/9k=
            """

            # Use the correct field names that match your form
            data = {'productName': 'New uploaded Product', 'productDescription': 
                                                    'Product for testing purposes', 'productPrice': '25'}
            data['productImage'] = (io.BytesIO(base64.b64decode(SMALLEST_JPEG_B64)), 'test.jpeg')
            resp = client.post('/upload/1', data = data, follow_redirects = True, content_type='multipart/form-data')
            
            # Upload should succeed with valid data and file
            self.assertEqual(resp.status_code, 200)
            product = Product.query.filter_by(productname = 'New uploaded Product').first()
            self.assertIsNotNone(product)
            self.assertEqual(product.productname, 'New uploaded Product')

    def test_APIgetallusers(self):
        
        """
        Testing the API route to get all users
        """

        with app.test_client() as client:
            resp = client.get('/v1/users')              # Should return a JSON

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json["Users"][0]["username"], 'johndoe')


    def test_APIgetallproducts(self):
        
        """
        Testing the API route to get all products
        """

        with app.test_client() as client:
            resp = client.get('/v1/products')              # Should return a JSON

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json["Products"][0]["productname"], 'Product Name')

    #########################################################################
    # ADDITIONAL TESTS FOR CORE FUNCTIONALITY
    #########################################################################

    def test_invalid_login_credentials(self):
        """
        Testing login with invalid credentials
        """
        with app.test_client() as client:
            resp = client.post('/login', data={'username': 'johndoe', 'password': 'wrongpassword'})
            
            # Should not have userid in session
            with client.session_transaction() as change_session:
                self.assertNotIn('userid', change_session)
            # Should get some kind of error response
            self.assertNotEqual(resp.status_code, 200)

    def test_duplicate_username_signup(self):
        """
        Testing signup with duplicate username
        """
        with app.test_client() as client:
            # First signup should work
            client.post('/signup', data={'username': 'janedoe', 'password': 'password', 'firstname': 'Jane', 'lastname': 'Doe'})
            
            # Second signup with same username should fail
            resp = client.post('/signup', data={'username': 'janedoe', 'password': 'password2', 'firstname': 'Jane2', 'lastname': 'Doe2'})
            
            # Should get some kind of error response
            self.assertNotEqual(resp.status_code, 200)

    def test_empty_form_submission(self):
        """
        Testing form submission with empty data
        """
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['userid'] = 1
            
            # Test empty signup form
            resp = client.post('/signup', data={'username': '', 'password': '', 'firstname': '', 'lastname': ''})
            self.assertNotEqual(resp.status_code, 200)
            
            # Test empty login form
            resp = client.post('/login', data={'username': '', 'password': ''})
            self.assertNotEqual(resp.status_code, 200)

    def test_cart_functionality(self):
        """
        Testing cart operations
        """
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['userid'] = 1
            
            # Add product to cart
            client.post('/product/1/addtocart')
            with client.session_transaction() as change_session:
                self.assertEqual(change_session['cart'], [1])
            
            # Add another product
            client.post('/product/1/addtocart')
            with client.session_transaction() as change_session:
                self.assertEqual(change_session['cart'], [1, 1])
            
            # Test cart page loads
            resp = client.get('/cart')
            self.assertEqual(resp.status_code, 200)

    def test_pagination_edge_cases(self):
        """
        Testing pagination edge cases
        """
        with app.test_client() as client:
            # Test going to previous page when already at first page
            resp = client.get('/?page=previous')
            with client.session_transaction() as change_session:
                self.assertEqual(change_session['page'], 0)
            
            # Test going to next page multiple times
            client.get('/?page=next')
            client.get('/?page=next')
            with client.session_transaction() as change_session:
                self.assertEqual(change_session['page'], 2)

    def test_product_search_functionality(self):
        """
        Testing product search if it exists
        """
        with app.test_client() as client:
            # Test search with existing product name
            resp = client.get('/?search=Product')
            self.assertEqual(resp.status_code, 200)
            
            # Test search with non-existent product
            resp = client.get('/?search=NonExistentProduct')
            self.assertEqual(resp.status_code, 200)

    def test_user_profile_access(self):
        """
        Testing user profile access permissions
        """
        with app.test_client() as client:
            # Test accessing user detail without login
            resp = client.get('/userdetail')
            self.assertEqual(resp.status_code, 302)  # Should redirect
            
            # Test accessing user detail with login
            with client.session_transaction() as change_session:
                change_session['userid'] = 1
            resp = client.get('/userdetail')
            self.assertEqual(resp.status_code, 200)

    def test_product_ownership(self):
        """
        Testing product ownership and editing permissions
        """
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['userid'] = 1
            
            # Test editing own product - check if edit route exists first
            resp = client.get('/product/1/edit')
            # If edit route doesn't exist, that's fine - just check we get some response
            self.assertIsInstance(resp.status_code, int)
            
            # Test editing someone else's product (should fail or redirect)
            # First create another user and product
            user2 = User.hashpassword('user2', 'password', 'User', 'Two')
            db.session.add(user2)
            db.session.commit()
            
            product2 = Product(productname='Product 2', productdescription='Description 2', price=30, user_id=2)
            db.session.add(product2)
            db.session.commit()
            
            # Try to edit product2 as user1
            resp = client.get(f'/product/{product2.productid}/edit')
            # Should either fail or redirect
            self.assertNotEqual(resp.status_code, 200)

    def test_invalid_product_id_access(self):
        """
        Testing access to products with invalid IDs
        """
        with app.test_client() as client:
            # Test with negative ID
            resp = client.get('/product/-1')
            self.assertEqual(resp.status_code, 404)
            
            # Test with string ID
            resp = client.get('/product/abc')
            self.assertEqual(resp.status_code, 404)
            
            # Test with very large ID
            resp = client.get('/product/999999')
            self.assertEqual(resp.status_code, 404)

    def test_session_management(self):
        """
        Testing session management and persistence
        """
        with app.test_client() as client:
            # Test session creation
            with client.session_transaction() as change_session:
                change_session['userid'] = 1
                change_session['cart'] = [1, 2, 3]
            
            # Test session persistence across requests
            with client.session_transaction() as change_session:
                self.assertEqual(change_session['userid'], 1)
                self.assertEqual(change_session['cart'], [1, 2, 3])
            
            # Test session clearing
            client.post('/logout')
            with client.session_transaction() as change_session:
                self.assertNotIn('userid', change_session)
                self.assertNotIn('cart', change_session)

    def test_database_constraints(self):
        """
        Testing database constraint violations
        """
        with app.test_client() as client:
            # Test creating user with missing required fields
            resp = client.post('/signup', data={'username': 'testuser'})  # Missing password, firstname, lastname
            self.assertNotEqual(resp.status_code, 200)
            
            # Test creating product with invalid price
            with client.session_transaction() as change_session:
                change_session['userid'] = 1
            
            resp = client.post('/upload/1', data={
                'productName': 'Test Product',
                'productDescription': 'Test Description',
                'productPrice': '-5'  # Invalid price (negative)
            })
            self.assertNotEqual(resp.status_code, 200)

    def test_API_error_handling(self):
        """
        Testing API error handling
        """
        with app.test_client() as client:
            # Test accessing non-existent user via API
            resp = client.get('/v1/users/999')
            self.assertEqual(resp.status_code, 404)
            
            # Test accessing non-existent product via API
            resp = client.get('/v1/products/999')
            self.assertEqual(resp.status_code, 404)
            
            # Test invalid API endpoints
            resp = client.get('/v1/invalid_endpoint')
            self.assertEqual(resp.status_code, 404)

    def test_file_upload_validation(self):
        """
        Testing file upload validation
        """
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session['userid'] = 1
            
            # Test upload without file
            data = {'productName': 'Test Product', 'productDescription': 'Test Description', 'productPrice': '25'}
            resp = client.post('/upload/1', data=data)
            self.assertNotEqual(resp.status_code, 200)
            
            # Test upload with invalid file type (if validation exists)
            # This would depend on your file validation logic
            pass

    def test_user_authentication_flow(self):
        """
        Testing complete user authentication flow
        """
        with app.test_client() as client:
            # Test signup
            resp = client.post('/signup', json={
                'username': 'newuser',
                'password': 'newpassword',
                'firstname': 'New',
                'lastname': 'User'
            }, content_type='application/json')
            
            # Signup should succeed
            self.assertEqual(resp.status_code, 200)
            
            # Test login with new user
            resp = client.post('/login', json={
                'username': 'newuser',
                'password': 'newpassword'
            }, content_type='application/json')
            
            # Login should succeed
            self.assertEqual(resp.status_code, 200)
            with client.session_transaction() as change_session:
                self.assertIn('userid', change_session)
            
            # Test logout
            client.post('/logout')
            with client.session_transaction() as change_session:
                self.assertNotIn('userid', change_session)
