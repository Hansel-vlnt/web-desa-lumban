from flask import Blueprint, render_template
from app.models import Gallery

gallery_bp = Blueprint('gallery', __name__)

@gallery_bp.route('/galeri')
def gallery_view():
    images = Gallery.query.filter_by(is_active=True).order_by(Gallery.created_at.desc()).all()
    categories = ['desa', 'wisata', 'budaya', 'kuliner']
    return render_template('public/gallery.html', images=images, categories=categories)