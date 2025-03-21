from ..extensions import db
from datetime import datetime

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valuer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)