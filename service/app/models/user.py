from datetime import datetime

from .number import Number
from .post import Post
from ..extensions import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin): # создаём модель пользователя
    id = db.Column(db.Integer, primary_key=True) # у него будет айдишник
    flag_id = db.Column(db.String(20), unique=True)
    posts = db.relationship(Post, backref='seller') # связь с моделью Post через backref параметр seller
    status = db.Column(db.String(50), default='user')
    flag = db.Column(db.String(200), unique=True, nullable=False)
    avatar = db.Column(db.String(200))
    name = db.Column(db.String(80))  # у него будет имя (Это поле мы используем в routes.py)
    login = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)