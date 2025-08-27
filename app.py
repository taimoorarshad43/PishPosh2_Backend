import os

from flask import Flask
from flask_cors import CORS, cross_origin
from flask_debugtoolbar import DebugToolbarExtension
from dotenv import load_dotenv
import redis

from models import connect_db

load_dotenv()                               # Load environmental variables

# Creating an application factory
def create_app(db_uri):                                 # Having the db_uri as an argument allows us to pass in different databases for testing/configuration
    app = Flask(__name__)

    with app.app_context(): # Need this for Flask 3
        connect_db(app, db_uri)

    return app

# db_uri = os.environ.get("SUPABASE_DATABASE_URI")
db_uri = "postgresql:///pishposh"
# db_uri = "postgresql:///unittest_debugging_test"

app = create_app(db_uri)

app.json.sort_keys = False                  # Prevents Flask from sorting keys in API JSON responses.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "seekrat"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

########### Flask-Session with Redis ###########

# Redis session configuration
app.config['SESSION_TYPE'] = 'redis' # filesystem, memcached, redis, etc.
app.config['SESSION_REDIS'] = redis.from_url("redis://localhost:6379")
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_SECURE'] = True # This fixed race condition issue.
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_PERMANENT'] = False

app.config['SESSION_KEY_PREFIX'] = 'session:'  # How Redis keys are prefixed
app.config['SESSION_USE_SIGNER'] = True        # Sign session cookies for security
app.config['SESSION_COOKIE_NAME'] = 'session'  # Explicitly set cookie name
app.config['SESSION_COOKIE_DOMAIN'] = None     # Allow cross-subdomain cookies
app.config['SESSION_COOKIE_MAX_AGE'] = 3600    # 1 hour session lifetime

# Initialize Flask-Session
from flask_session import Session
server_session = Session(app)

####################################################################

# Import blueprints AFTER app and session are created
from blueprints.apiroutes import apiroutes
from blueprints.checkout import productcheckout
from blueprints.cart import cartroutes
from blueprints.product import productroutes
from blueprints.userroutes import userroutes
from blueprints.uploadroutes import uploadroutes
from blueprints.indexroutes import indexroutes

# Register blueprints AFTER session is initialized
app.register_blueprint(apiroutes, url_prefix = "/v1")
app.register_blueprint(productcheckout)
app.register_blueprint(cartroutes)
app.register_blueprint(productroutes)
app.register_blueprint(userroutes)
app.register_blueprint(uploadroutes)
app.register_blueprint(indexroutes)

toolbar = DebugToolbarExtension(app)

########### CORS Configuration ###########

CORS(app, 
     supports_credentials=True, 
     origins=["http://127.0.0.1:5173", "http://localhost:5173"],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Set-Cookie"],
     credentials=True
)

####################################################################