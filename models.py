from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from random import randint
import base64

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app, db_uri):                        # Inits the app context with supplied db_uri
    """Connect to database."""

    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri

    db.app = app
    db.init_app(app)
    db.create_all()
    # db.drop_all() # For debugging if we want to start with a new table each time

class User(db.Model):

    """User model with username, first name, last name, and hashedpassword"""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    username = db.Column(db.String(50),
                         nullable = False,
                         unique = True)

    passwordhash = db.Column(db.String,
                             nullable = False)
    
    firstname = db.Column(db.String(50), nullable = False)
    lastname = db.Column(db.String(50))

    products = db.relationship("Product", backref = 'user', cascade = 'all, delete-orphan')

    def fullname(self):
        return self.firstname + " " + self.lastname

    @classmethod
    def hashpassword(cls, username, password, firstname, lastname):

        """
        Hashes inputted password and returns user instance with hashedpassword in password field

        """

        hashpw = bcrypt.generate_password_hash(password)
        hashedpw_utf8 = hashpw.decode('utf8')

        return cls(username=username, passwordhash=hashedpw_utf8, firstname=firstname, lastname=lastname)
    
    @classmethod
    def authenticate(cls, username, password):

        """
        Checking if user is in fact there and checking if password matches.
        
        Returns user if True and returns False if check fails
        """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.passwordhash, password):
            return user
        else:
            return False


class Product(db.Model):

    """Product model with product ID, product name, product description, and user ID as a foreign key"""


    __tablename__ = 'products'

    productid = db.Column(db.Integer,
                          primary_key = True,
                          autoincrement=True)
    
    productname = db.Column(db.String(200),
                            nullable = False)
    
    productdescription = db.Column(db.String,
                                   nullable = True)
    price = db.Column(db.Integer,
                      nullable = False)
    
    image = db.Column(db.LargeBinary)
    
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'
                                      , ondelete = 'cascade'
                                      ))

    @classmethod
    def generateprice(cls):
        """Generate random integer prices from 1 to 100"""
        price = randint(1,100)

        return price

    def encode_image(self, image_data):
        """Encodes image data to binary for storage."""
        image_data = base64.b64encode(image_data)

        self.image = image_data


    def decode_image(self):
        """Decodes binary image data to string for display in HTML. Returns image or None if no image attribute"""
        if self.image:
            return self.image.decode('utf-8')

        return None
    

class Tag(db.Model):

    """Tagging/Category Model with tag ID, tag name, product name as foreign key"""

    __tablename__ = 'tags'

    tagid = db.Column(db.Integer,
                      primary_key = True,
                      autoincrement = True)
    
    tagname = db.Column(db.String(50),
                        nullable = False)

    products = db.relationship('Product',
                               secondary = 'products_tags',
                               backref = 'tags')
    

class ProductTag(db.Model):

    """Join table for Products/Tags with tags.tagid and products.productid as primary composite keys"""

    __tablename__ = 'products_tags'

    tagid = db.Column(db.Integer,
                      db.ForeignKey('tags.tagid',
                        ondelete = 'cascade'),
                         primary_key = True)

    productid = db.Column(db.Integer,
                          db.ForeignKey('products.productid',
                        ondelete = 'cascade'),
                          primary_key = True)
