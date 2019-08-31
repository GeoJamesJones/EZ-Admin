from datetime import datetime
from hashlib import md5
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Base user model that is used to create the schema im the SQLite database.
# This class is used extensive throughout the application.


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    portal_url = db.Column(db.String(500), index=True)
    portal_username = db.Column(db.String(128), index=True)
    portal_password = db.Column(db.String(128))
    portal_name = db.Column(db.String(128), index=True)

    # Returns how the user model will be represented when printed
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def followed_posts(self):
        own = Post.query.filter_by(
            user_id=self.id).order_by(Post.timestamp.desc())
        return own


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# Post model used to create the Posts table in the SQLite database.
# The posts is used as means of tracking application functions and when
# they were last ran.  Acts as a high level log.
# Logging is handled seperately.
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
