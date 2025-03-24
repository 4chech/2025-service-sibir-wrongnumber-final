from ..extensions import db
from datetime import datetime

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))
    valuer_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    rating = db.Column(db.Integer)  
    comment = db.Column(db.String(500))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.id}>'