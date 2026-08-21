from app import create_app, db
from werkzeug.security import generate_password_hash
from app.models import Admin, Category, Place, Ulos, UlosPhoto, Gallery, VillageInfo
import os

app = create_app()

def seed_all():
    with app.app_context():
        print("="*60)
        print("🌾 SEEDING DATA - KAMPUNG ULOS")
        print("="*60)
        
        # ===== 1. ADMIN =====
        print("\n📝 Creating admin...")
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(
                username='admin',
                email='admin@kampungulos.com',
                password_hash=generate_password_hash('password123'),
                full_name='Administrator Desa',
                role='super_admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin created (admin / password123)")
        
        # ===== 2. CATEGORIES =====
        print("\n📝 Creating categories...")
        categories = [
            {'name': 'Wisata', 'slug': 'wisata', 'icon': 'fa-map-marked-alt', 'description': 'Destinasi wisata'},
            {'name': 'Homestay', 'slug': 'homestay', 'icon': 'fa-bed', 'description': 'Penginapan'},
            {'name': 'UMKM', 'slug': 'umkm', 'icon': 'fa-store', 'description_text': 'Usaha Mikro Kecil Menengah'},
            {'name': 'Kuliner', 'slug': 'kuliner', 'icon': 'fa-utensils', 'description': 'Kuliner'},
        ]
        for cat_data in categories:
            cat = Category.query.filter_by(slug=cat_data['slug']).first()
            if not cat:
                cat = Category(**cat_data)
                db.session.add(cat)
        db.session.commit()
        print("✅ Categories created")
        
        # ===== 3. VILLAGE INFO =====
        print("\n📝 Creating village info...")
        sejarah = VillageInfo.query.filter_by(type='sejarah').first()
        if not sejarah:
            sejarah = VillageInfo(
                title='Sejarah Desa',
                content='<h4>Sejarah Desa Lumban Suhi-Suhi Toruan</h4><p>Desa ini adalah pusat kerajinan tenun ulos...</p>',
                type='sejarah',
                is_active=True
            )
            db.session.add(sejarah)
        db.session.commit()
        print("✅ Village info created")
        
        # ===== 4. PLACES =====
        print("\n📝 Creating places...")
        wisata_cat = Category.query.filter_by(slug='wisata').first()
        if wisata_cat:
            place = Place.query.filter_by(slug='kampung-ulos').first()
            if not place:
                place = Place(
                    name='Kampung Ulos',
                    slug='kampung-ulos',
                    category_id=wisata_cat.id,
                    description='<h4>Pusat Kerajinan Tenun Ulos</h4>',
                    address='Desa Lumban Suhi-Suhi Toruan',
                    is_active=True,
                    created_by=admin.id
                )
                db.session.add(place)
        db.session.commit()
        print("✅ Places created")
        
        # ===== 5. ULOS with PHOTOS & AUDIO =====
        print("\n📝 Creating ULOS with photos and audio...")
        
        # === PATH YANG BENAR ===
        # Foto: /static/uploads/ulos/nama-file.jpg
        # Audio: /static/uploads/audio/nama-file.mp3
        
        ulos_data = [
            {
                'name': 'ULOS Bintang Maratur',
                'slug': 'ulos-bintang-maratur',
                'motif_description': '<h4>Motif Bintang</h4><p>Motif bintang tersusun rapi.</p>',
                'meaning': '<h4>Filosofi</h4><p>Melambangkan kehidupan harmonis.</p>',
                'function': '<h4>Fungsi</h4><p>Upacara adat besar.</p>',
                'qr_code': 'ULOS-BM-004',
                'is_active': True,
                'photos': ['ulos-bintang-maratur.jpg'],  # Nama file foto
                'audio_id': 'ulos-bintang-maratur-id.mp3',  # Nama file audio ID
                'audio_en': 'ulos-bintang-maratur-en.mp3'   # Nama file audio EN
            }
        ]
        
        for item in ulos_data:
            existing = Ulos.query.filter_by(qr_code=item['qr_code']).first()
            
            if not existing:
                ulos = Ulos(
                    name=item['name'],
                    slug=item['slug'],
                    motif_description=item['motif_description'],
                    meaning=item['meaning'],
                    function=item['function'],
                    qr_code=item['qr_code'],
                    is_active=item['is_active'],
                    # === PASTIKAN PATH INI BENAR ===
                    audio_indonesia='/static/uploads/audio/' + item['audio_id'],
                    audio_english='/static/uploads/audio/' + item['audio_en']
                )
                db.session.add(ulos)
                db.session.flush()
                
                # Tambah foto
                for idx, photo in enumerate(item['photos']):
                    ulos_photo = UlosPhoto(
                        ulos_id=ulos.id,
                        photo_path='/static/uploads/ulos/' + photo,
                        is_primary=(idx == 0),
                        sort_order=idx
                    )
                    db.session.add(ulos_photo)
                    print(f"   📸 Added photo: {photo}")
                
                print(f"   🎵 Added audio ID: {item['audio_id']}")
                print(f"   🎵 Added audio EN: {item['audio_en']}")
                print(f"   ✅ {item['name']} created")
            else:
                print(f"   ⏭️  {item['name']} already exists")
        
        db.session.commit()
        print("✅ ULOS created")


        # =========================================================
        # ===== 6. GALLERY (TAMBAHKAN INI) =====
        # =========================================================
        print("\n📝 Creating gallery images for hero...")
        
        gallery_data = [
            {
                'title': 'Background Hero',
                'caption': 'Gambar latar belakang utama Desa Wisata',
                'category': 'hero_background',
                'photo_path': '/static/uploads/gallery/hero-background.MOV',
                'is_active': True
            },
            {
                'title': 'Hero Image',
                'caption': 'Gambar samping judul Desa Wisata',
                'category': 'hero',
                'photo_path': '/static/uploads/gallery/hero-image.jpg',
                'is_active': True
            }
        ]
        
        for gallery_item in gallery_data:
            existing = Gallery.query.filter_by(title=gallery_item['title']).first()
            if not existing:
                gallery = Gallery(**gallery_item)
                db.session.add(gallery)
                print(f"   📸 Added gallery: {gallery_item['title']} ({gallery_item['category']})")
            else:
                print(f"   ⏭️  {gallery_item['title']} already exists")
        
        db.session.commit()
        print("✅ Gallery created")
        

        print("\n" + "="*60)
        print("🎉 SEEDING COMPLETE!")
        print("="*60)
        print("\n🔑 Login Admin:")
        print("   URL: http://localhost:5000/login")
        print("   Username: admin")
        print("   Password: password123")
        print("\n📁 Pastikan file ada di:")
        print("   app/static/uploads/ulos/ulos-bintang-maratur.jpg")
        print("   app/static/uploads/audio/ulos-bintang-maratur-id.mp3")
        print("   app/static/uploads/audio/ulos-bintang-maratur-en.mp3")
        print("   app/static/uploads/gallery/hero-background.jpg  ← BARU")
        print("   app/static/uploads/gallery/hero-image.jpg       ← BARU")
        print("="*60)

if __name__ == '__main__':
    seed_all()