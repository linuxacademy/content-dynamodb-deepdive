import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)

app.config['SECRET_KEY'] = '056e0820604e3c45b8908388be1fcaf8'
app.s3_prefix = os.environ['S3_PREFIX']
print(f" * Album art using S3 bucket prefix {app.s3_prefix}")

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from webapp import routes  # must be the last line
