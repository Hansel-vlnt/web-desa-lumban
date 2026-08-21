from app import db
from datetime import datetime

class UlosPhoto(db.Model):
    __tablename__ = 'ulos_photos'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    ulos_id = db.Column(db.Integer, db.ForeignKey('ulos.id'), nullable=False)
    photo_path = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(200))
    is_primary = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UlosPhoto {self.ulos_id}>'