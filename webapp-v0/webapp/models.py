import os

from flask_login import UserMixin

from webapp import app, db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    albums = db.relationship('Album', backref='artist', lazy=True)

    def __repr__(self):
        return f"Artist('{self.name}')"


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(255), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        "artist.id"), nullable=False)
    title = db.Column(db.String(1024), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    format = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    tracks = db.relationship('Track', backref='Album', lazy=True)

    @property
    def album_art(self):
        id_album = list(str(self.id))
        id_album.reverse()
        filepath = '/'.join(id_album)
        albumart = os.path.join(app.static_folder, 'albumart')
        filename = os.path.join(albumart, filepath, f'{self.id}.jpg')

        if os.path.exists(filename) and (os.path.getsize(filename) > 0):
            return f"/static/albumart/{filepath}/{self.id}.jpg"
        else:
            return "/static/img/no-albumart.svg"

    def __repr__(self):
        return f"Album('{self.name}')"


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey("album.id"), nullable=False)
    name = db.Column(db.String(2048))
    length = db.Column(db.Integer, nullable=True)
    number = db.Column(db.String(3), nullable=True)

    @property
    def length_str(self):
        try:
            s = self.length / 1000
            m, s = divmod(s, 60)
            return f"{m:.0f}:{s:02.0f}"
        except TypeError:
            return "(track length unavailable)"


def __repr__(self):
    return f"Track('{self.name}')"
