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

app.config.update(
    {
        "S3_PREFIX": os.environ["S3_PREFIX"],
        # Cognito
        "COGNITO_REGION": os.environ["COGNITO_REGION"],
        "COGNITO_DOMAIN": os.environ["COGNITO_DOMAIN"],
        "COGNITO_USERPOOL_ID": os.environ["COGNITO_USERPOOL_ID"],
        "COGNITO_APP_CLIENT_ID": os.environ["COGNITO_APP_CLIENT_ID"],
        "COGNITO_APP_CLIENT_SECRET": os.environ["COGNITO_APP_CLIENT_SECRET"],
        # Amazon
        "AMAZON_APP_CLIENT_ID": os.environ["AMAZON_APP_CLIENT_ID"],
        "AMAZON_APP_CLIENT_SECRET": os.environ["AMAZON_APP_CLIENT_SECRET"],
        # Google API
        "GOOGLE_APP_CLIENT_ID": os.environ["GOOGLE_APP_CLIENT_ID"],
        "GOOGLE_APP_CLIENT_SECRET": os.environ["GOOGLE_APP_CLIENT_SECRET"],
    }
)

app.logger.info(f'Album art using S3 bucket prefix {app.config["S3_PREFIX"]}')

# Cache Cognito keys once at startup
try:
    keys_url = "https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json".format(
        app.config["COGNITO_REGION"], app.config["COGNITO_USERPOOL_ID"]
    )
    keys_response = urllib.request.urlopen(keys_url)
    keys = json.loads(keys_response.read())["keys"]
    app.config["COGNITO_KEYS"] = keys
    app.logger.debug(f"Cognito keys: {keys}")
except urllib.error.URLError as e:
    app.logger.error("Could not load Cognito keys:", e.reason)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

# this line must be last in this file to avoid circular imports
from webapp import routes  # noqa: F401,E402
