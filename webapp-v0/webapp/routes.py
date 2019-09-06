from flask import flash, redirect, render_template, request, url_for
from flask_caching import Cache
from flask_login import current_user, login_required, login_user, logout_user

from webapp import app, bcrypt, db
from webapp.forms import LoginForm, RegistrationForm, UpdateAccountForm
from webapp.models import Album, Artist, Track, User

config = {
    "DEBUG": True,           # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}
app.config.from_mapping(config)
cache = Cache(app)


@app.route("/")
def index():
    return redirect('/home')


@app.route("/home")
@cache.cached(timeout=300, query_string=True)
def home():
    page = request.args.get('page', 1, type=int)
    albums = Album.query.order_by(
        Album.year.desc(), Album.price.asc()).paginate(page=page, per_page=9)
    return render_template('home.html', albums=albums, next_num=page + 1, prev_num=page - 1)


@app.route('/album/<int:id>')
@cache.cached(timeout=300)
def album_by_id(id):
    album = Album.query.get(id)
    return render_template('album.html', album=album)


@app.route('/artist/<int:id>')
@cache.cached(timeout=300)
def artist_by_id(id):
    artist = Artist.query.get(id)
    albums = Album.query.filter_by(artist_id=id).order_by(Album.year.desc())
    return render_template('artist.html', artist=artist, albums=albums)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/about")
@cache.cached(timeout=300)
def about():
    return render_template('about.html')


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)


@app.route("/results")
@cache.cached(timeout=300, query_string=True)
def results():
    page = request.args.get('page', 1, type=int)
    entity_type = request.args['entity_type']
    term = request.args['term']

    if entity_type == 'artist':
        albums = Album.query.join(Artist).filter(
            Artist.name == term).paginate(page=page, per_page=9)
        return render_template('results.html', albums=albums, term=term,
                               entity_type=entity_type, next_num=page + 1,
                               prev_num=page - 1)
    elif entity_type == 'album':
        albums = Album.query.filter(Album.title.like(term + "%")).paginate(
            page=page, per_page=9)
        return render_template('results.html', albums=albums, term=term,
                               entity_type=entity_type, next_num=page + 1,
                               prev_num=page - 1)
    elif entity_type == 'track':
        albums = Album.query.join(Track).filter(
            Track.name == term).paginate(page=page, per_page=9)
        return render_template('results.html', albums=albums, term=term,
                               entity_type=entity_type, next_num=page + 1,
                               prev_num=page - 1)
