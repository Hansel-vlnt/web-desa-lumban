from flask import Blueprint, render_template, request
from app.models import Place, Category, Review, PlacePhoto
from app import db

places_bp = Blueprint('places', __name__)

@places_bp.route('/wisata')
def places_list():
    category_slug = request.args.get('kategori')
    search = request.args.get('cari')
    
    query = Place.query.filter_by(is_active=True)
    
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first()
        if category:
            query = query.filter_by(category_id=category.id)
    
    if search:
        query = query.filter(
            Place.name.contains(search) | 
            Place.description.contains(search)
        )
    
    places = query.order_by(Place.created_at.desc()).all()
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template(
        'public/places.html',
        places=places,
        categories=categories,
        active_category=category_slug
    )


@places_bp.route('/wisata/<string:slug>')
def place_detail(slug):
    place = Place.query.filter_by(slug=slug, is_active=True).first_or_404()
    reviews = Review.query.filter_by(place_id=place.id, is_verified=True).order_by(
        Review.created_at.desc()
    ).all()
    
    # ===== AMBIL FOTO SLIDE =====
    slide_photos = PlacePhoto.query.filter_by(place_id=place.id).order_by(
        PlacePhoto.sort_order
    ).all()
    
    print(f"📸 {place.name} - Jumlah file slide: {len(slide_photos)}")
    for p in slide_photos:
        print(f"   - {p.photo_path} (video: {p.is_video})")
    # =============================
    
    avg_rating = db.session.query(db.func.avg(Review.rating)).filter(
        Review.place_id == place.id,
        Review.is_verified == True
    ).scalar() or 0
    
    return render_template(
        'public/place_detail.html',
        place=place,
        reviews=reviews,
        avg_rating=round(avg_rating, 1),
        slide_photos=slide_photos
    )