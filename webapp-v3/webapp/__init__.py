import json
import os
import urllib

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)

load_dotenv(verbose=True)

app.config["SECRET_KEY"] = "056e0820604e3c45b8908388be1fcaf8"
app.config["S3_PREFIX"] = os.environ["S3_PREFIX"]

app.logger.info(f'Album art using S3 bucket prefix {app.config["S3_PREFIX"]}')

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

# this line must be last in this file to avoid circular imports
from webapp import routes  # noqa: F401,E402
