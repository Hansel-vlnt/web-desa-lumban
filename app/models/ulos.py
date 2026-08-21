from app import db
from datetime import datetime

class Ulos(db.Model):
    __tablename__ = 'ulos'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    motif_description = db.Column(db.Text)
    motif_description_text = db.Column(db.Text)
    meaning = db.Column(db.Text)
    meaning_text = db.Column(db.Text)
    function = db.Column(db.Text)
    function_text = db.Column(db.Text)
    qr_code = db.Column(db.String(100), unique=True, nullable=False)
    audio_indonesia = db.Column(db.String(500))
    audio_english = db.Column(db.String(500))
    audio_batak = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    photos = db.relationship('UlosPhoto', backref='ulos', lazy=True, cascade='all, delete-orphan')
    
    def _format_text(self, text, label='🌐 English Version'):
        """Format teks dengan [EN] menjadi HTML"""
        if not text or not text.strip():
            return '<p>Belum tersedia</p>'
        
        if '[EN]' in text:
            parts = text.split('[EN]')
            indo_part = parts[0].strip() if len(parts) > 0 else ''
            en_part = parts[1].strip() if len(parts) > 1 else ''
            
            html = ''
            
            # Bahasa Indonesia
            if indo_part:
                paragraphs = indo_part.split('\n')
                paragraphs = [p.strip() for p in paragraphs if p.strip()]
                html += ''.join([f'<p class="text-indonesia">{p}</p>' for p in paragraphs])
            
            # Bahasa Inggris (bersatu dalam wrapper)
            if en_part:
                paragraphs = en_part.split('\n')
                paragraphs = [p.strip() for p in paragraphs if p.strip()]
                html += f'''
                <div class="en-wrapper">
                    <div class="en-label">{label}</div>
                    {''.join([f'<p class="text-english">{p}</p>' for p in paragraphs])}
                </div>
                '''
            
            return html
        else:
            paragraphs = text.split('\n')
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            return ''.join([f'<p>{p}</p>' for p in paragraphs])
    
    def get_motif_html(self):
        return self._format_text(self.motif_description_text or self.motif_description, '🌐 Motif (English)')
    
    def get_meaning_html(self):
        return self._format_text(self.meaning_text or self.meaning, '🌐 Filosofi (English)')
    
    def get_function_html(self):
        return self._format_text(self.function_text or self.function, '🌐 Kegunaan (English)')
    
    def get_all_photos(self):
        photos = []
        for photo in self.photos:
            photos.append(photo.photo_path)
        return photos
    
    def __repr__(self):
        return f'<Ulos {self.name}>'