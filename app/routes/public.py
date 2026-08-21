from flask import Blueprint, render_template, request
from app.models import Place, Ulos, Gallery, VillageInfo, Category
from app import cache

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
@cache.cached(timeout=300)
def index():
    """Landing Page"""
    hero_image = Gallery.query.filter_by(is_active=True, category='hero').first()
    if not hero_image:
        hero_image = Gallery.query.filter_by(is_active=True).first()
    
    # ===== AMBIL LOGO =====
    logo_desa = Gallery.query.filter_by(is_active=True, category='logo').first()
    logo_bumdes = Gallery.query.filter_by(is_active=True, category='logo_bumdes').first()
    
    print(f"Logo Desa: {logo_desa.photo_path if logo_desa else 'Tidak ditemukan'}")
    print(f"Logo BUMDES: {logo_bumdes.photo_path if logo_bumdes else 'Tidak ditemukan'}")
    # ======================
    
    sejarah = VillageInfo.query.filter_by(type='sejarah', is_active=True).first()
    pemerintahan = VillageInfo.query.filter_by(type='pemerintahan', is_active=True).first()
    featured_ulos = Ulos.query.filter_by(is_active=True).limit(6).all()
    all_places = Place.query.filter_by(is_active=True).all()
    ulos_count = Ulos.query.filter_by(is_active=True).count()
    
    return render_template(
        'public/index.html',
        hero_image=hero_image,
        logo_desa=logo_desa,
        logo_bumdes=logo_bumdes,
        sejarah=sejarah,
        pemerintahan=pemerintahan,
        featured_ulos=featured_ulos,
        all_places=all_places,
        ulos_count=ulos_count
    )


@public_bp.route('/tentang')
def about():
    """About page"""
    sejarah = VillageInfo.query.filter_by(type='sejarah', is_active=True).first()
    visi_misi = VillageInfo.query.filter_by(type='visi_misi', is_active=True).first()
    pemerintahan = VillageInfo.query.filter_by(type='pemerintahan', is_active=True).first()
    
    return render_template(
        'public/about.html',
        sejarah=sejarah,
        visi_misi=visi_misi,
        pemerintahan=pemerintahan
    )


@public_bp.route('/wisata-alam')
@cache.cached(timeout=300)
def wisata_alam():
    """Halaman Wisata Alam dengan 2 section: Lumban Manik dan Huta Raja"""
    
    lumban_manik = {
        'wisata': Place.query.filter_by(
            destination_group='lumban_manik', 
            place_type='wisata', 
            is_active=True
        ).all(),
        'homestay': Place.query.filter_by(
            destination_group='lumban_manik', 
            place_type='homestay', 
            is_active=True
        ).all(),
        'umkm': Place.query.filter_by(
            destination_group='lumban_manik', 
            place_type='umkm', 
            is_active=True
        ).all()
    }
    
    huta_raja = {
        'wisata': Place.query.filter_by(
            destination_group='huta_raja', 
            place_type='wisata', 
            is_active=True
        ).all(),
        'homestay': Place.query.filter_by(
            destination_group='huta_raja', 
            place_type='homestay', 
            is_active=True
        ).all(),
        'umkm': Place.query.filter_by(
            destination_group='huta_raja', 
            place_type='umkm', 
            is_active=True
        ).all()
    }
    
    return render_template(
        'public/wisata_alam.html',
        lumban_manik=lumban_manik,
        huta_raja=huta_raja
    )


@public_bp.route('/homestay')
@cache.cached(timeout=300)
def homestay_list():
    """Halaman semua Homestay"""
    homestays = Place.query.filter_by(place_type='homestay', is_active=True).all()
    print(f"🏠 Jumlah homestay: {len(homestays)}")
    for h in homestays:
        print(f"   - {h.name}: {len(h.photos)} foto")
    
    return render_template('public/homestay_list.html', homestays=homestays)


@public_bp.route('/umkm')
@cache.cached(timeout=300)
def umkm_list():
    """Halaman semua UMKM"""
    umkms = Place.query.filter_by(place_type='umkm', is_active=True).all()
    return render_template('public/umkm_list.html', umkms=umkms)