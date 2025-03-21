from datetime import datetime

from sqlalchemy.orm import backref

from .number import Number
from ..extensions import db


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    number_id = db.Column(db.Integer, db.ForeignKey('number.id', ondelete='SET NULL'))
    car_mark = db.Column(db.String(250))
    picture = db.Column(db.String(200))
    price = db.Column(db.String(250))
    valuer = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(250))
    speed = db.Column(db.Float)
    handling = db.Column(db.Float)
    durability = db.Column(db.Float)
    fuel_consumption = db.Column(db.Float)
    seating_capacity = db.Column(db.Integer)
    customizations = db.Column(db.String(250))
    number = db.relationship(Number, backref="post")