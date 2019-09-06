import os
import pprint
import sys
from datetime import datetime

import requests
from flask import abort, redirect, render_template, request, session, url_for
from flask_caching import Cache
from flask_login import login_required, login_user, logout_user
from requests.auth import HTTPBasicAuth

from webapp import app, login_manager
from webapp.cognito import hosted_ui_url, verify_token
from webapp.models import Album, Artist, User

config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
}
app.config.from_mapping(config)
app.add_template_global(hosted_ui_url, name="hosted_ui_url")
cache = Cache(app)

PAGE_SIZE = 9


@login_manager.user_loader
def user_loader(session_token):
    """Populate user object, check expiry"""
    if "expires" not in session:
        return None

    expires = datetime.utcfromtimestamp(session["expires"])
    expires_seconds = (expires - datetime.utcnow()).total_seconds()
    if expires_seconds < 0:
        return None

    user = User()
    user.id = session_token
    user.nickname = session["nickname"]
    return user


@app.route("/")
def index():
    return redirect("/home")


@app.route("/home")
# @cache.cached(timeout=300, query_string=True)
def home():
    last_evaluated_key = request.args.get("last_evaluated_key", None, type=str)
    prev_evaluated_key = request.args.get("prev_evaluated_key", None, type=str)
    albums, last_evaluated_key, prev_evaluated_key = Album.get_all(
        prev_evaluated_key, last_evaluated_key, PAGE_SIZE
    )
    return render_template(
        "home.html",
        albums=albums,
        last_evaluated_key=last_evaluated_key,
        prev_evaluated_key=prev_evaluated_key,
    )


@app.route("/album/<int:id>")
@cache.cached(timeout=300)
def album_by_id(id):
    album = Album.get_by_id(id)
    return render_template("album.html", album=album)


@app.route("/artist/<int:id>")
@cache.cached(timeout=300)
def artist_by_id(id):
    artist = Artist.get_by_id(id)
    return render_template("artist.html", artist=artist, albums=artist.albums)


@app.route("/login")
def login():
    # http://docs.aws.amazon.com/cognito/latest/developerguide/login-endpoint.html
    session["csrf_state"] = os.urandom(8).hex()
    cognito_login = hosted_ui_url(state=session["csrf_state"])
    return redirect(cognito_login)


@app.route("/signup")
def signup():
    # https://pinehead.auth.us-east-1.amazoncognito.com/signup?response_type=code&client_id=24ftcdanu65gufq324de69hkif&redirect_uri=https://localhost:5000/callback&state=348cea3dc8a7c32f
    session["csrf_state"] = os.urandom(8).hex()
    cognito_signup = hosted_ui_url("signup", state=session["csrf_state"])
    return redirect(cognito_signup)


@app.route("/logout")
@login_required
def logout():
    # http://docs.aws.amazon.com/cognito/latest/developerguide/logout-endpoint.html
    logout_user()
    cognito_logout = hosted_ui_url("logout")
    return redirect(cognito_logout)


@app.route("/callback", methods=["GET", "POST"])
def callback():
    """Exchange the 'code' for a Cognito token"""
    # http://docs.aws.amazon.com/cognito/latest/developerguide/token-endpoint.html
    app.logger.debug(pprint.pformat(request.__dict__, depth=5))
    csrf_state = request.args.get("state")
    code = request.args.get("code")

    request_parameters = {
        "grant_type": "authorization_code",
        "client_id": app.config["COGNITO_APP_CLIENT_ID"],
        "code": code,
        "redirect_uri": f"https://{request.headers['Host']}/callback",
    }

    response = requests.post(
        f"https://{app.config['COGNITO_DOMAIN']}/oauth2/token",
        data=request_parameters,
        auth=HTTPBasicAuth(
            app.config["COGNITO_APP_CLIENT_ID"], app.config["COGNITO_APP_CLIENT_SECRET"]
        ),
    )

    # the response:
    # http://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html
    # and csrf_state == session['csrf_state']:
    if response.status_code == 200 and csrf_state == session["csrf_state"]:
        response_json = response.json()
        verify_token(response_json["access_token"])
        id_token = verify_token(
            response_json["id_token"], response_json["access_token"]
        )

        user = User()
        user.id = id_token["cognito:username"]
        session["nickname"] = id_token["email"]
        session["expires"] = id_token["exp"]
        session["refresh_token"] = response_json["refresh_token"]
        login_user(user, remember=True)
        return redirect(url_for("home"))
    else:
        abort(401)


@app.route("/about")
@cache.cached(timeout=300)
def about():
    return render_template("about.html")


@app.route("/results")
@cache.cached(timeout=300, query_string=True)
def results():

    last_evaluated_key = request.args.get("last_evaluated_key", None, type=str)
    prev_evaluated_key = request.args.get("prev_evaluated_key", None, type=str)
    entity_type = request.args["entity_type"]
    term = request.args["term"]

    if entity_type == "artist":
        artists = Artist.find_by_name(term)
        return render_template("artist-results.html", artists=artists, term=term)
    elif entity_type == "album":
        albums, last_evaluated_key, prev_evaluated_key = Album.find_by_title(
            term, prev_evaluated_key, last_evaluated_key, PAGE_SIZE
        )
        return render_template(
            "results.html",
            albums=albums,
            term=term,
            entity_type=entity_type,
            last_evaluated_key=last_evaluated_key,
            prev_evaluated_key=prev_evaluated_key,
        )
    elif entity_type == "track":
        albums = Album.find_by_track(term)
        return render_template(
            "results.html", albums=albums, term=term, entity_type=entity_type
        )


@app.route("/info")
@login_required
def info():
    "Webserver info route"
    metadata = "http://169.254.169.254"
    instance_id = requests.get(metadata + "/latest/meta-data/instance-id").text
    availability_zone = requests.get(
        metadata + "/latest/meta-data/placement/availability-zone"
    ).text

    return render_template(
        "info.html",
        instance_id=instance_id,
        availability_zone=availability_zone,
        sys_version=sys.version,
    )


@app.errorhandler(401)
def access_denied(e):
    return render_template("401.html"), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
