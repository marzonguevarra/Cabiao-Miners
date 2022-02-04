from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
from flask_msearch import Search
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from vonage import vonage


client = vonage.Client(key="d0ec6aac", secret="A56jvJwtgb114evh")
sms = vonage.Sms(client)

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cabiaominer.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/dbcabiaominers'
app.config['SECRET_KEY']='ramlnyangforeversserdf'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# image upload
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
search = Search()
search.init_app(app)

migrate = Migrate(app, db)
with app.app_context():
    if db.engine.url.drivername == "sqlite":
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='customerLogin'
login_manager.needs_refresh_messsage_category='danger'
login_manager.login_message = u"Please login first"

from main.routes import admin,customers,products,carts