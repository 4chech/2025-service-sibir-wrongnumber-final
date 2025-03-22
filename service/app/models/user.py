from datetime import datetime

from .number import Number
from .post import Post
from ..extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posts = db.relationship(Post, backref='seller')
    status = db.Column(db.String(50), default='user')
    flag = db.Column(db.String(200), unique=True, nullable=False)
    avatar = db.Column(db.String(200))
    name = db.Column(db.String(80))
    login = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)