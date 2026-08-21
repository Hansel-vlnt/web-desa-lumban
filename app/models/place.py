from app import db
from datetime import datetime
from sqlalchemy import Numeric

class Place(db.Model):
    __tablename__ = 'places'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    description_text = db.Column(db.Text)
    address = db.Column(db.Text)
    latitude = db.Column(Numeric(10, 8))
    longitude = db.Column(Numeric(11, 8))
    google_maps_url = db.Column(db.String(500))
    whatsapp_number = db.Column(db.String(20))
    opening_hours = db.Column(db.String(200))
    photo_path = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    destination_group = db.Column(db.String(50), default='umum')
    place_type = db.Column(db.String(50), default='wisata')
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reviews = db.relationship('Review', backref='place', lazy=True, cascade='all, delete-orphan')
    photos = db.relationship('PlacePhoto', backref='place', lazy=True, cascade='all, delete-orphan')
    
    def get_description_html(self):
        """Memproses [EN] menjadi HTML dengan 2 bahasa"""
        text = self.description_text or self.description or ''
        
        if not text or not text.strip():
            return '<p>Deskripsi belum tersedia</p>'
        
        # ===== PROSES [EN] =====
        if '[EN]' in text:
            parts = text.split('[EN]')
            indo_part = parts[0].strip() if len(parts) > 0 else ''
            en_part = parts[1].strip() if len(parts) > 1 else ''
            
            html = ''
            
            # ===== BAHASA INDONESIA =====
            if indo_part:
                # Pisahkan menjadi paragraf berdasarkan newline
                paragraphs = indo_part.split('\n')
                # Filter paragraf kosong
                paragraphs = [p.strip() for p in paragraphs if p.strip()]
                html += ''.join([f'<p class="text-indonesia">{p}</p>' for p in paragraphs])
            
            # ===== BAHASA INGGRIS (RAPI & BERSATU) =====
            if en_part:
                # Pisahkan menjadi paragraf berdasarkan newline
                paragraphs = en_part.split('\n')
                # Filter paragraf kosong
                paragraphs = [p.strip() for p in paragraphs if p.strip()]
                # Gabungkan semua paragraf dalam satu div
                html += f'''
                <div class="en-wrapper">
                    <div class="en-label">🌐 English Version</div>
                    {''.join([f'<p class="text-english">{p}</p>' for p in paragraphs])}
                </div>
                '''
            
            return html
        else:
            # ===== TANPA [EN] =====
            paragraphs = text.split('\n')
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            return ''.join([f'<p>{p}</p>' for p in paragraphs])
    
    def get_all_photos(self):
        photos = []
        if self.photo_path:
            photos.append(self.photo_path)
        for photo in self.photos:
            photos.append(photo.photo_path)
        return photos
    
    def __repr__(self):
        return f'<Place {self.name}>'