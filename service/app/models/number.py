from ..extensions import db


class Number(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(200), unique=False)
    secret = db.Column(db.String(200), db.ForeignKey('user.flag', ondelete='CASCADE'), unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner_login = db.Column(db.String(50), db.ForeignKey('user.login', ondelete='CASCADE'))
