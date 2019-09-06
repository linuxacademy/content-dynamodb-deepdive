from flask import request
from jose import jwt

from webapp import app


def hosted_ui_url(action="login", response_type="code", state=""):

    url = (
        f"https://{app.config['COGNITO_DOMAIN']}/{action}"
        f"?response_type={response_type}"
        f"&client_id={app.config['COGNITO_APP_CLIENT_ID']}"
        f"&state={state}"
        f"&redirect_uri=https://{request.headers['Host']}/callback"
    )

    # https://developer.amazon.com/docs/login-with-amazon/authorization-code-grant.html#authorization-request
    if action == "signup":
        url += "&scope=openid profile"

    # For 'Login with Amazon', the redirect URI for the Cognito User Pool
    # must be set up in the Amazon Developer portal
    # Log into: https://developer.amazon.com/settings/console/securityprofile/web-settings/update.html
    # add to 'Allowed Return URLs': https://<your app name>.auth.us-east-1.amazoncognito.com/oauth2/idpresponse

    return url


def verify_token(token, access_token=None):
    """Verify a cognito JWT"""
    # get the key id from the header, locate it in the cognito keys
    # and verify the key
    header = jwt.get_unverified_header(token)
    jwks = app.config["COGNITO_KEYS"]
    audience = app.config["COGNITO_APP_CLIENT_ID"]
    key = [k for k in jwks if k["kid"] == header["kid"]][0]
    id_token = jwt.decode(token, key, audience=audience, access_token=access_token)
    return id_token
