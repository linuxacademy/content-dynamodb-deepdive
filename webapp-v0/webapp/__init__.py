from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = '056e0820604e3c45b8908388be1fcaf8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://pinehead:pinehead@localhost/pinehead'
app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from webapp import routes  # must be the last line
