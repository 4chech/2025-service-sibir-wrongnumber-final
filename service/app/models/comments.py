from ..extensions import db
from datetime import datetime

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))
    #valuer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    valuer_login = db.Column(db.String(50), db.ForeignKey('user.login', ondelete='CASCADE'))
    comment = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)