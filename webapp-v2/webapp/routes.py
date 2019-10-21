from flask import flash, redirect, render_template, request, url_for
from flask_caching import Cache
from flask_login import current_user, login_required, login_user, logout_user

from webapp import app, bcrypt
from webapp.forms import LoginForm, RegistrationForm, UpdateAccountForm
from webapp.models import Album, Artist, User

config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
}
app.config.from_mapping(config)
cache = Cache(app)

PAGE_SIZE = 9


@app.route("/")
def index():
    return redirect("/home")


@app.route("/home")
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


@app.route("/artist/<name>/album/<int:id>")
def album_by_id(name, id):
    album = Album.get_by_id(name, id)
    return render_template("album.html", album=album)


@app.route("/artist/<name>/album/<title>")
def album_by_artist_and_title(name, title):
    album = Album.find_by_artist_and_title(name, title)
    return render_template("album.html", album=album)


@app.route("/artist/<name>")
def artist_by_name(name):
    albums = Artist.find_by_name(name)
    return render_template("artist.html", albums=albums, artist_name=name)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(email=form.email.data, password=hashed_password)

        user.add()

        flash("Your account has been created! You are now able to log in", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_user(form.email.data)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/about")
@cache.cached(timeout=300)
def about():
    return render_template("about.html")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.update()
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.email.data = current_user.email
    return render_template("account.html", title="Account", form=form)


@app.route("/results")
def results():

    last_evaluated_key = request.args.get("last_evaluated_key", None, type=str)
    prev_evaluated_key = request.args.get("prev_evaluated_key", None, type=str)
    entity_type = request.args["entity_type"]
    term = request.args["term"]

    if entity_type == "artist":
        albums = Artist.find_by_name(term)
        # print(dir(albums))
        return render_template("artist-results.html", albums=albums, term=term)
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


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
