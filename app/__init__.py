from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_caching import Cache
from werkzeug.security import check_password_hash
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cache = Cache()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cache.init_app(app)
    
    login_manager.login_view = 'login'
    login_manager.login_message = 'Silakan login'
    
    from app.models import Admin
    
    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))
    
    # =========================================================
    # CONTEXT PROCESSOR - LOGO UNTUK SEMUA TEMPLATE
    # =========================================================
    @app.context_processor
    def inject_logo():
        from app.models import Gallery
        try:
            logo_desa = Gallery.query.filter_by(is_active=True, category='logo').first()
            logo_bumdes = Gallery.query.filter_by(is_active=True, category='logo_bumdes').first()
            return dict(logo_desa=logo_desa, logo_bumdes=logo_bumdes)
        except:
            return dict(logo_desa=None, logo_bumdes=None)
    
    # =========================================================
    # ROUTE LANDING PAGE - /
    # =========================================================
    @app.route('/')
    def index():
        try:
            from app.models import Place, Ulos, Gallery, VillageInfo
            
            hero_image = Gallery.query.filter_by(category='hero', is_active=True).first()
            if not hero_image:
                hero_image = Gallery.query.filter_by(is_active=True).first()
            
            hero_background = Gallery.query.filter_by(category='hero_background', is_active=True).first()
            
            sejarah = VillageInfo.query.filter_by(type='sejarah', is_active=True).first()
            pemerintahan = VillageInfo.query.filter_by(type='pemerintahan', is_active=True).first()
            featured_ulos = Ulos.query.filter_by(is_active=True).limit(6).all()
            all_places = Place.query.filter_by(is_active=True).all()
            ulos_count = Ulos.query.filter_by(is_active=True).count()
            
            return render_template(
                'public/index.html',
                hero_image=hero_image,
                hero_background=hero_background,
                sejarah=sejarah,
                pemerintahan=pemerintahan,
                featured_ulos=featured_ulos,
                all_places=all_places,
                ulos_count=ulos_count
            )
        except Exception as e:
            return f"<h1>Error di landing page</h1><p>{str(e)}</p>", 500
    
    # =========================================================
    # ROUTE LOGIN - /login
    # =========================================================
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            admin = Admin.query.filter_by(username=username).first()
            
            if admin and check_password_hash(admin.password_hash, password):
                login_user(admin)
                return redirect(url_for('dashboard'))
            else:
                flash('Username atau password salah', 'danger')
        
        return render_template('admin/login.html')
    
    # =========================================================
    # ROUTE DASHBOARD - /dashboard
    # =========================================================
    @app.route('/dashboard')
    @login_required
    def dashboard():
        from app.models import Place, Ulos, Review, Category, Gallery
        
        total_places = Place.query.count()
        total_ulos = Ulos.query.count()
        total_reviews = Review.query.filter_by(is_verified=True).count()
        total_categories = Category.query.count()
        total_gallery = Gallery.query.count()
        
        recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(10).all()
        recent_places = Place.query.order_by(Place.created_at.desc()).limit(5).all()
        
        return render_template(
            'admin/dashboard.html',
            total_places=total_places,
            total_ulos=total_ulos,
            total_reviews=total_reviews,
            total_categories=total_categories,
            total_gallery=total_gallery,
            recent_reviews=recent_reviews,
            recent_places=recent_places
        )
    
    # =========================================================
    # ROUTE LOGOUT - /logout
    # =========================================================
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Anda telah logout', 'info')
        return redirect(url_for('login'))
    
    # =========================================================
    # ROUTE WISATA ALAM - /wisata-alam
    # =========================================================
    @app.route('/wisata-alam')
    def wisata_alam():
        from app.models import Place
        
        lumban_manik = Place.query.filter_by(destination_group='lumban_manik', is_active=True).all()
        huta_raja = Place.query.filter_by(destination_group='huta_raja', is_active=True).all()
        
        return render_template(
            'public/wisata_alam.html',
            lumban_manik={'wisata': lumban_manik, 'homestay': [], 'umkm': []},
            huta_raja={'wisata': huta_raja, 'homestay': [], 'umkm': []}
        )
    
    # =========================================================
    # ROUTE HOMESTAY - /homestay
    # =========================================================
    @app.route('/homestay')
    def homestay_list():
        from app.models import Place
        homestays = Place.query.filter_by(place_type='homestay', is_active=True).all()
        return render_template('public/homestay_list.html', homestays=homestays)
    
    # =========================================================
    # ROUTE UMKM - /umkm
    # =========================================================
    @app.route('/umkm')
    def umkm_list():
        from app.models import Place
        umkms = Place.query.filter_by(place_type='umkm', is_active=True).all()
        return render_template('public/umkm_list.html', umkms=umkms)
    
    # =========================================================
    # ROUTE ULOS GALERI - /ulos
    # =========================================================
    @app.route('/ulos')
    def ulos_gallery():
        from app.models import Ulos
        ulos_list = Ulos.query.filter_by(is_active=True).all()
        return render_template('public/ulos_gallery.html', ulos_list=ulos_list)
    
    # =========================================================
    # ROUTE ULOS DETAIL BY QR - /ulos/<qr_code>
    # =========================================================
    @app.route('/ulos/<string:qr_code>')
    def ulos_detail_by_qr(qr_code):
        from app.models import Ulos, UlosPhoto
        ulos = Ulos.query.filter_by(qr_code=qr_code, is_active=True).first_or_404()
        photos = UlosPhoto.query.filter_by(ulos_id=ulos.id).all()
        return render_template('public/ulos_detail.html', ulos=ulos, photos=photos)
    
    # =========================================================
    # ROUTE PLAY AUDIO - /ulos/audio/<ulos_id>/<language>
    # =========================================================
    @app.route('/ulos/audio/<int:ulos_id>/<string:language>')
    def play_audio(ulos_id, language):
        from app.models import Ulos
        from flask import send_file, jsonify, current_app
        import os
        
        ulos = Ulos.query.get_or_404(ulos_id)
        
        if language == 'id':
            audio_path_str = ulos.audio_indonesia
        elif language == 'en':
            audio_path_str = ulos.audio_english
        elif language == 'batak':
            audio_path_str = ulos.audio_batak
        else:
            return jsonify({'error': 'Bahasa tidak tersedia'}), 404
        
        if not audio_path_str:
            return jsonify({'error': 'Audio tidak tersedia'}), 404
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filename = os.path.basename(audio_path_str)
        full_path = os.path.join(upload_folder, 'audio', filename)
        
        if not os.path.exists(full_path):
            return jsonify({'error': 'File audio tidak ditemukan'}), 404
        
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        mime_types = {
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'm4a': 'audio/mp4',
            'ogg': 'audio/ogg',
            'mp4': 'audio/mp4',
            'mpeg': 'audio/mpeg',
            'aac': 'audio/aac',
            'flac': 'audio/flac',
        }
        mime_type = mime_types.get(ext, 'audio/mpeg')
        
        return send_file(full_path, mimetype=mime_type, as_attachment=False)
    
    # =========================================================
    # ROUTE ADMIN - CRUD
    # =========================================================

    # ===== KATEGORI =====
    @app.route('/admin/categories')
    @login_required
    def admin_categories():
        from app.models import Category
        categories = Category.query.order_by(Category.name).all()
        return render_template('admin/categories.html', categories=categories)

    @app.route('/admin/categories/add', methods=['POST'])
    @login_required
    def admin_add_category():
        from app.models import Category
        from app.utils.helpers import Helpers
        
        name = request.form.get('name')
        icon = request.form.get('icon', 'fa-tag')
        description = request.form.get('description', '')
        
        if not name:
            flash('Nama kategori wajib diisi', 'danger')
            return redirect(url_for('admin_categories'))
        
        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash('Kategori sudah ada', 'warning')
            return redirect(url_for('admin_categories'))
        
        category = Category(
            name=name,
            slug=Helpers.generate_slug(name),
            icon=icon,
            description=description
        )
        db.session.add(category)
        db.session.commit()
        flash('Kategori berhasil ditambahkan', 'success')
        return redirect(url_for('admin_categories'))

    @app.route('/admin/categories/edit/<int:id>', methods=['POST'])
    @login_required
    def admin_edit_category(id):
        from app.models import Category
        from app.utils.helpers import Helpers
        
        category = Category.query.get_or_404(id)
        
        name = request.form.get('name')
        icon = request.form.get('icon', category.icon)
        description = request.form.get('description', category.description)
        is_active = request.form.get('is_active') == 'on'
        
        if not name:
            flash('Nama kategori wajib diisi', 'danger')
            return redirect(url_for('admin_categories'))
        
        category.name = name
        category.slug = Helpers.generate_slug(name)
        category.icon = icon
        category.description = description
        category.is_active = is_active
        db.session.commit()
        flash('Kategori berhasil diupdate', 'success')
        return redirect(url_for('admin_categories'))

    @app.route('/admin/categories/delete/<int:id>', methods=['POST'])
    @login_required
    def admin_delete_category(id):
        from app.models import Category
        category = Category.query.get_or_404(id)
        
        if category.places:
            flash('Kategori tidak bisa dihapus karena masih memiliki tempat wisata', 'danger')
            return redirect(url_for('admin_categories'))
        
        db.session.delete(category)
        db.session.commit()
        flash('Kategori berhasil dihapus', 'success')
        return redirect(url_for('admin_categories'))

    # ===== TEMPAT WISATA =====
    @app.route('/admin/places')
    @login_required
    def admin_places():
        from app.models import Place
        places = Place.query.order_by(Place.created_at.desc()).all()
        return render_template('admin/places.html', places=places)

    # ============================================================
    # ===== PERBAIKI: admin_add_place (description_text) =====
    # ============================================================
    @app.route('/admin/places/add', methods=['GET', 'POST'])
    @login_required
    def admin_add_place():
        from app.models import Place, Category, PlacePhoto
        from app.utils.helpers import Helpers
        from flask import current_app
        
        categories = Category.query.filter_by(is_active=True).all()
        
        if request.method == 'POST':
            print("="*70)
            print("🔍 ADMIN ADD PLACE - ALL FORM DATA:")
            for key, value in request.form.items():
                print(f"   {key}: {value[:100] if value else 'KOSONG'}")
            print("="*70)
            
            name = request.form.get('name')
            category_id = request.form.get('category_id')
            # ===== PERBAIKI: AMBIL description_text =====
            description_text = request.form.get('description_text', '')
            address = request.form.get('address')
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            google_maps_url = request.form.get('google_maps_url')
            whatsapp_number = request.form.get('whatsapp_number')
            opening_hours = request.form.get('opening_hours')
            destination_group = request.form.get('destination_group')
            place_type = request.form.get('place_type')
            is_active = request.form.get('is_active') == 'on'
            
            print(f"📝 DESCRIPTION_TEXT: {description_text[:100] if description_text else 'KOSONG!'}")
            
            if not name or not category_id:
                flash('Nama dan kategori wajib diisi', 'danger')
                return redirect(url_for('admin_add_place'))
            
            photo_path = None
            photo_file = request.files.get('photo')
            if photo_file and photo_file.filename:
                if Helpers.allowed_file(photo_file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                    photo_path = Helpers.save_uploaded_file(photo_file, current_app.config['UPLOAD_FOLDER'], 'places')
                else:
                    flash('Format file tidak didukung', 'danger')
                    return redirect(url_for('admin_add_place'))
            
            place = Place(
                name=name,
                slug=Helpers.generate_slug(name),
                category_id=category_id,
                description_text=description_text,
                description=description_text.replace('\n', '<br>') if description_text else '',
                address=address,
                latitude=latitude if latitude else None,
                longitude=longitude if longitude else None,
                google_maps_url=google_maps_url,
                whatsapp_number=whatsapp_number,
                opening_hours=opening_hours,
                photo_path=photo_path,
                destination_group=destination_group,
                place_type=place_type,
                created_by=current_user.id,
                is_active=is_active
            )
            
            db.session.add(place)
            db.session.commit()
            
            # ===== UPLOAD SLIDE PHOTOS =====
            slide_files = request.files.getlist('slide_photos')
            print(f"📸 Jumlah file slide: {len(slide_files)}")
            
            for idx, file in enumerate(slide_files):
                if file and file.filename:
                    print(f"   - File: {file.filename}")
                    is_video = Helpers.is_video_file(file.filename) if hasattr(Helpers, 'is_video_file') else False
                    
                    if Helpers.allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']) or is_video:
                        file_path = Helpers.save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'], 'places')
                        place_photo = PlacePhoto(
                            place_id=place.id,
                            photo_path=file_path,
                            is_primary=(idx == 0),
                            sort_order=idx,
                            is_video=is_video
                        )
                        db.session.add(place_photo)
                        print(f"   ✅ Slide {idx} disimpan: {file_path}")
                    else:
                        print(f"   ❌ Format tidak didukung: {file.filename}")
            db.session.commit()
            
            saved = Place.query.get(place.id)
            print(f"✅ SETELAH SAVE: description_text = {saved.description_text[:50] if saved.description_text else 'KOSONG!'}")
            print("="*70)
            
            flash('Tempat wisata berhasil ditambahkan!', 'success')
            return redirect(url_for('admin_places'))
        
        return render_template('admin/place_form.html', categories=categories, place=None)

    # ============================================================
    # ===== PERBAIKI: admin_edit_place (description_text) =====
    # ============================================================
    @app.route('/admin/places/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def admin_edit_place(id):
        from app.models import Place, Category, PlacePhoto
        from app.utils.helpers import Helpers
        from flask import current_app
        import os
        
        place = Place.query.get_or_404(id)
        categories = Category.query.filter_by(is_active=True).all()
        
        if request.method == 'POST':
            print("="*60)
            print("🔍 ADMIN EDIT PLACE - METHOD POST")
            print("="*60)
            
            print("📝 ALL FORM DATA:")
            for key, value in request.form.items():
                print(f"   {key}: {value[:100] if value else 'KOSONG'}")
            print("="*60)
            
            name = request.form.get('name')
            category_id = request.form.get('category_id')
            # ===== PERBAIKI: AMBIL description_text =====
            description_text = request.form.get('description_text', '')
            address = request.form.get('address')
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            google_maps_url = request.form.get('google_maps_url')
            whatsapp_number = request.form.get('whatsapp_number')
            opening_hours = request.form.get('opening_hours')
            destination_group = request.form.get('destination_group')
            place_type = request.form.get('place_type')
            is_active = request.form.get('is_active') == 'on'
            
            print(f"📝 DESCRIPTION_TEXT DARI FORM: {description_text[:100] if description_text else 'KOSONG!'}")
            print("="*60)
            
            if not name or not category_id:
                flash('Nama dan kategori wajib diisi', 'danger')
                return redirect(url_for('admin_edit_place', id=id))
            
            # ===== UPDATE FOTO UTAMA =====
            photo_file = request.files.get('photo')
            if photo_file and photo_file.filename:
                print(f"📸 Foto utama: {photo_file.filename}")
                if Helpers.allowed_file(photo_file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                    if place.photo_path:
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], place.photo_path.replace('/static/uploads/', ''))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    photo_path = Helpers.save_uploaded_file(photo_file, current_app.config['UPLOAD_FOLDER'], 'places')
                    place.photo_path = photo_path
                    print(f"   ✅ Path: {photo_path}")
                else:
                    flash('Format file tidak didukung', 'danger')
                    return redirect(url_for('admin_edit_place', id=id))
            
            # ===== UPDATE DATA =====
            place.name = name
            place.slug = Helpers.generate_slug(name)
            place.category_id = category_id
            place.description_text = description_text
            place.description = description_text.replace('\n', '<br>') if description_text else ''
            place.address = address
            place.latitude = latitude if latitude else None
            place.longitude = longitude if longitude else None
            place.google_maps_url = google_maps_url
            place.whatsapp_number = whatsapp_number
            place.opening_hours = opening_hours
            place.destination_group = destination_group
            place.place_type = place_type
            place.is_active = is_active
            
            db.session.commit()
            
            # ============================================================
            # ===== TAMBAH FOTO SLIDE (TANPA MENGHAPUS) =====
            # ============================================================
            slide_files = request.files.getlist('slide_photos')
            slide_files = [f for f in slide_files if f and f.filename]
            
            if slide_files:
                last_order = PlacePhoto.query.filter_by(place_id=place.id).order_by(PlacePhoto.sort_order.desc()).first()
                start_order = (last_order.sort_order + 1) if last_order else 0
                
                for idx, file in enumerate(slide_files):
                    print(f"   File {idx}: {file.filename}")
                    is_video = Helpers.is_video_file(file.filename) if hasattr(Helpers, 'is_video_file') else False
                    
                    if Helpers.allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']) or is_video:
                        file_path = Helpers.save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'], 'places')
                        place_photo = PlacePhoto(
                            place_id=place.id,
                            photo_path=file_path,
                            is_primary=False,
                            sort_order=start_order + idx,
                            is_video=is_video
                        )
                        db.session.add(place_photo)
                        print(f"   ✅ Slide {idx} ditambahkan: {file_path}")
                    else:
                        print(f"   ❌ Format tidak didukung: {file.filename}")
            # ============================================================
            
            # ===== HAPUS FOTO YANG DIPILIH =====
            remove_photo_ids = request.form.getlist('remove_photos')
            if remove_photo_ids:
                for photo_id in remove_photo_ids:
                    photo = PlacePhoto.query.get(int(photo_id))
                    if photo and photo.place_id == place.id:
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.photo_path.replace('/static/uploads/', ''))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                        db.session.delete(photo)
                        print(f"   🗑️ Foto {photo_id} dihapus")
            # ==================================
            
            db.session.commit()
            
            saved = Place.query.get(place.id)
            print(f"✅ SETELAH SAVE: description_text = {saved.description_text[:50] if saved.description_text else 'KOSONG!'}")
            print("="*60)
            
            flash('Tempat wisata berhasil diupdate!', 'success')
            return redirect(url_for('admin_places'))
        
        return render_template('admin/place_form.html', place=place, categories=categories)

    @app.route('/admin/places/delete/<int:id>', methods=['POST'])
    @login_required
    def admin_delete_place(id):
        from app.models import Place
        place = Place.query.get_or_404(id)
        db.session.delete(place)
        db.session.commit()
        flash('Tempat wisata berhasil dihapus', 'success')
        return redirect(url_for('admin_places'))

    @app.route('/admin/places/photo/delete/<int:id>', methods=['POST'])
    @login_required
    def admin_delete_place_photo(id):
        from app.models import PlacePhoto
        photo = PlacePhoto.query.get_or_404(id)
        place_id = photo.place_id
        db.session.delete(photo)
        db.session.commit()
        flash('Foto berhasil dihapus', 'success')
        return redirect(url_for('admin_edit_place', id=place_id))

    # ===== ULOS =====
    @app.route('/admin/ulos')
    @login_required
    def admin_ulos():
        from app.models import Ulos
        ulos_list = Ulos.query.order_by(Ulos.created_at.desc()).all()
        return render_template('admin/ulos_list.html', ulos_list=ulos_list)

    # ============================================================
    # ===== PERBAIKI: admin_add_ulos (_text fields) =====
    # ============================================================
    @app.route('/admin/ulos/add', methods=['GET', 'POST'])
    @login_required
    def admin_add_ulos():
        from app.models import Ulos, UlosPhoto
        from app.utils.helpers import Helpers
        from app.utils.qr_generator import QRGenerator
        from flask import current_app
        
        if request.method == 'POST':
            print("="*70)
            print("🔍 ADMIN ADD ULOS - ALL FORM DATA:")
            for key, value in request.form.items():
                print(f"   {key}: {value[:100] if value else 'KOSONG'}")
            print("="*70)
            
            name = request.form.get('name')
            # ===== PERBAIKI: AMBIL _text fields =====
            motif_description_text = request.form.get('motif_description_text', '')
            meaning_text = request.form.get('meaning_text', '')
            function_text = request.form.get('function_text', '')
            
            print(f"📝 motif_description_text: {motif_description_text[:100] if motif_description_text else 'KOSONG!'}")
            print(f"📝 meaning_text: {meaning_text[:100] if meaning_text else 'KOSONG!'}")
            print(f"📝 function_text: {function_text[:100] if function_text else 'KOSONG!'}")
            
            if not name:
                flash('Nama ULOS wajib diisi', 'danger')
                return redirect(url_for('admin_add_ulos'))
            
            qr_code = QRGenerator.generate_unique_code(name)
            
            ulos = Ulos(
                name=name,
                slug=Helpers.generate_slug(name),
                motif_description_text=motif_description_text,
                motif_description=motif_description_text.replace('\n', '<br>') if motif_description_text else '',
                meaning_text=meaning_text,
                meaning=meaning_text.replace('\n', '<br>') if meaning_text else '',
                function_text=function_text,
                function=function_text.replace('\n', '<br>') if function_text else '',
                qr_code=qr_code
            )
            
            db.session.add(ulos)
            db.session.commit()
            
            # Upload Foto
            photos = request.files.getlist('photos')
            for idx, photo in enumerate(photos):
                if photo and photo.filename:
                    if Helpers.allowed_file(photo.filename, current_app.config['ALLOWED_EXTENSIONS']):
                        photo_path = Helpers.save_uploaded_file(photo, current_app.config['UPLOAD_FOLDER'], 'ulos')
                        ulos_photo = UlosPhoto(
                            ulos_id=ulos.id,
                            photo_path=photo_path,
                            is_primary=(idx == 0),
                            sort_order=idx
                        )
                        db.session.add(ulos_photo)
            
            # Upload Audio - Indonesia
            audio_id = request.files.get('audio_id')
            if audio_id and audio_id.filename:
                if Helpers.allowed_file(audio_id.filename, current_app.config['ALLOWED_AUDIO_EXTENSIONS']):
                    audio_path = Helpers.save_uploaded_file(audio_id, current_app.config['UPLOAD_FOLDER'], 'audio')
                    ulos.audio_indonesia = audio_path
            
            # Upload Audio - Inggris
            audio_en = request.files.get('audio_en')
            if audio_en and audio_en.filename:
                if Helpers.allowed_file(audio_en.filename, current_app.config['ALLOWED_AUDIO_EXTENSIONS']):
                    audio_path = Helpers.save_uploaded_file(audio_en, current_app.config['UPLOAD_FOLDER'], 'audio')
                    ulos.audio_english = audio_path
            
            # Upload Audio - Batak
            audio_batak = request.files.get('audio_batak')
            if audio_batak and audio_batak.filename:
                if Helpers.allowed_file(audio_batak.filename, current_app.config['ALLOWED_AUDIO_EXTENSIONS']):
                    audio_path = Helpers.save_uploaded_file(audio_batak, current_app.config['UPLOAD_FOLDER'], 'audio')
                    ulos.audio_batak = audio_path
            
            db.session.commit()
            QRGenerator.generate_ulos_qr(ulos.id, ulos.name, ulos.qr_code)
            
            saved = Ulos.query.get(ulos.id)
            print(f"✅ SETELAH SAVE: motif_description_text = {saved.motif_description_text[:50] if saved.motif_description_text else 'KOSONG!'}")
            print(f"✅ SETELAH SAVE: meaning_text = {saved.meaning_text[:50] if saved.meaning_text else 'KOSONG!'}")
            print(f"✅ SETELAH SAVE: function_text = {saved.function_text[:50] if saved.function_text else 'KOSONG!'}")
            print("="*70)
            
            flash(f'ULOS berhasil ditambahkan! QR Code: {ulos.qr_code}', 'success')
            return redirect(url_for('admin_ulos'))
        
        return render_template('admin/ulos_form.html')

    # ============================================================
    # ===== PERBAIKI: admin_edit_ulos (_text fields) =====
    # ============================================================
    @app.route('/admin/ulos/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def admin_edit_ulos(id):
        from app.models import Ulos, UlosPhoto
        from app.utils.helpers import Helpers
        from flask import current_app
        import os
        
        ulos = Ulos.query.get_or_404(id)
        
        if request.method == 'POST':
            print("="*60)
            print("🔍 ADMIN EDIT ULOS - METHOD POST")
            print("="*60)
            
            print("📝 ALL FORM DATA:")
            for key, value in request.form.items():
                print(f"   {key}: {value[:100] if value else 'KOSONG'}")
            print("="*60)
            
            name = request.form.get('name')
            # ===== PERBAIKI: AMBIL _text fields =====
            motif_description_text = request.form.get('motif_description_text', '')
            meaning_text = request.form.get('meaning_text', '')
            function_text = request.form.get('function_text', '')
            is_active = request.form.get('is_active') == 'on'
            
            print(f"📝 motif_description_text: {motif_description_text[:100] if motif_description_text else 'KOSONG!'}")
            print(f"📝 meaning_text: {meaning_text[:100] if meaning_text else 'KOSONG!'}")
            print(f"📝 function_text: {function_text[:100] if function_text else 'KOSONG!'}")
            
            if not name:
                flash('Nama ULOS wajib diisi', 'danger')
                return redirect(url_for('admin_edit_ulos', id=id))
            
            # ===== UPDATE DATA =====
            ulos.name = name
            ulos.slug = Helpers.generate_slug(name)
            ulos.motif_description_text = motif_description_text
            ulos.motif_description = motif_description_text.replace('\n', '<br>') if motif_description_text else ''
            ulos.meaning_text = meaning_text
            ulos.meaning = meaning_text.replace('\n', '<br>') if meaning_text else ''
            ulos.function_text = function_text
            ulos.function = function_text.replace('\n', '<br>') if function_text else ''
            ulos.is_active = is_active
            
            # ============================================================
            # ===== TAMBAH FOTO (TANPA MENGHAPUS) =====
            # ============================================================
            photos = request.files.getlist('photos')
            photos = [f for f in photos if f and f.filename]
            
            if photos:
                last_order = UlosPhoto.query.filter_by(ulos_id=ulos.id).order_by(UlosPhoto.sort_order.desc()).first()
                start_order = (last_order.sort_order + 1) if last_order else 0
                
                for idx, photo in enumerate(photos):
                    print(f"   File {idx}: {photo.filename}")
                    
                    if Helpers.allowed_file(photo.filename, current_app.config['ALLOWED_EXTENSIONS']):
                        photo_path = Helpers.save_uploaded_file(photo, current_app.config['UPLOAD_FOLDER'], 'ulos')
                        ulos_photo = UlosPhoto(
                            ulos_id=ulos.id,
                            photo_path=photo_path,
                            is_primary=(len(ulos.photos) == 0 and idx == 0),
                            sort_order=start_order + idx
                        )
                        db.session.add(ulos_photo)
                        print(f"   ✅ Foto {idx} ditambahkan: {photo_path}")
                    else:
                        print(f"   ❌ Format tidak didukung: {photo.filename}")
            # ============================================================
            
            # ===== HAPUS FOTO YANG DIPILIH =====
            remove_photo_ids = request.form.getlist('remove_photos')
            if remove_photo_ids:
                for photo_id in remove_photo_ids:
                    photo = UlosPhoto.query.get(int(photo_id))
                    if photo and photo.ulos_id == ulos.id:
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.photo_path.replace('/static/uploads/', ''))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                        db.session.delete(photo)
                        print(f"   🗑️ Foto {photo_id} dihapus")
            # ==================================
            
            # ===== UPLOAD AUDIO =====
            audio_file = request.files.get('audio_id')
            if audio_file and audio_file.filename:
                ext = audio_file.filename.rsplit('.', 1)[1].lower() if '.' in audio_file.filename else ''
                if ext in current_app.config['ALLOWED_AUDIO_EXTENSIONS']:
                    if ulos.audio_indonesia:
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'audio', os.path.basename(ulos.audio_indonesia))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    audio_path = Helpers.save_uploaded_file(audio_file, current_app.config['UPLOAD_FOLDER'], 'audio')
                    ulos.audio_indonesia = audio_path
                    print(f"🎵 Audio Indonesia: {audio_path}")
            
            audio_file = request.files.get('audio_en')
            if audio_file and audio_file.filename:
                ext = audio_file.filename.rsplit('.', 1)[1].lower() if '.' in audio_file.filename else ''
                if ext in current_app.config['ALLOWED_AUDIO_EXTENSIONS']:
                    if ulos.audio_english:
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'audio', os.path.basename(ulos.audio_english))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    audio_path = Helpers.save_uploaded_file(audio_file, current_app.config['UPLOAD_FOLDER'], 'audio')
                    ulos.audio_english = audio_path
                    print(f"🎵 Audio Inggris: {audio_path}")
            
            audio_file = request.files.get('audio_batak')
            if audio_file and audio_file.filename:
                ext = audio_file.filename.rsplit('.', 1)[1].lower() if '.' in audio_file.filename else ''
                if ext in current_app.config['ALLOWED_AUDIO_EXTENSIONS']:
                    if ulos.audio_batak:
                        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'audio', os.path.basename(ulos.audio_batak))
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    audio_path = Helpers.save_uploaded_file(audio_file, current_app.config['UPLOAD_FOLDER'], 'audio')
                    ulos.audio_batak = audio_path
                    print(f"🎵 Audio Batak: {audio_path}")
            # =================================
            
            db.session.commit()
            
            saved = Ulos.query.get(ulos.id)
            print(f"✅ SETELAH SAVE: motif_description_text = {saved.motif_description_text[:50] if saved.motif_description_text else 'KOSONG!'}")
            print(f"✅ SETELAH SAVE: meaning_text = {saved.meaning_text[:50] if saved.meaning_text else 'KOSONG!'}")
            print(f"✅ SETELAH SAVE: function_text = {saved.function_text[:50] if saved.function_text else 'KOSONG!'}")
            print("="*60)
            
            flash('ULOS berhasil diupdate!', 'success')
            return redirect(url_for('admin_ulos'))
        
        return render_template('admin/ulos_form.html', ulos=ulos)

    @app.route('/admin/ulos/delete/<int:id>', methods=['POST'])
    @login_required
    def admin_delete_ulos(id):
        from app.models import Ulos
        ulos = Ulos.query.get_or_404(id)
        db.session.delete(ulos)
        db.session.commit()
        flash('ULOS berhasil dihapus', 'success')
        return redirect(url_for('admin_ulos'))

    @app.route('/admin/ulos/photo/delete/<int:id>', methods=['POST'])
    @login_required
    def admin_delete_ulos_photo(id):
        from app.models import UlosPhoto
        photo = UlosPhoto.query.get_or_404(id)
        ulos_id = photo.ulos_id
        db.session.delete(photo)
        db.session.commit()
        flash('Foto berhasil dihapus', 'success')
        return redirect(url_for('admin_edit_ulos', id=ulos_id))

    # ===== GALERI =====
    @app.route('/admin/gallery')
    @login_required
    def admin_gallery():
        from app.models import Gallery
        images = Gallery.query.order_by(Gallery.created_at.desc()).all()
        return render_template('admin/gallery.html', images=images)

    @app.route('/admin/gallery/add', methods=['POST'])
    @login_required
    def admin_add_gallery():
        from app.models import Gallery
        from app.utils.helpers import Helpers
        from flask import current_app
        
        title = request.form.get('title')
        caption = request.form.get('caption', '')
        category = request.form.get('category', 'desa')
        
        photo_file = request.files.get('photo')
        if not photo_file or not photo_file.filename:
            flash('Foto wajib diupload', 'danger')
            return redirect(url_for('admin_gallery'))
        
        if not Helpers.allowed_file(photo_file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            flash('Format file tidak didukung', 'danger')
            return redirect(url_for('admin_gallery'))
        
        photo_path = Helpers.save_uploaded_file(photo_file, current_app.config['UPLOAD_FOLDER'], 'gallery')
        
        gallery = Gallery(
            title=title or 'Gambar',
            photo_path=photo_path,
            caption=caption,
            category=category
        )
        db.session.add(gallery)
        db.session.commit()
        flash('Foto berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_gallery'))

    @app.route('/admin/gallery/edit/<int:id>', methods=['POST'])
    @login_required
    def admin_edit_gallery(id):
        from app.models import Gallery
        
        gallery = Gallery.query.get_or_404(id)
        
        title = request.form.get('title')
        caption = request.form.get('caption')
        category = request.form.get('category')
        is_active = request.form.get('is_active') == 'on'
        
        if title:
            gallery.title = title
        if caption:
            gallery.caption = caption
        if category:
            gallery.category = category
        gallery.is_active = is_active
        
        db.session.commit()
        flash('Galeri berhasil diupdate', 'success')
        return redirect(url_for('admin_gallery'))

    @app.route('/admin/gallery/delete/<int:id>', methods=['POST'])
    @login_required
    def admin_delete_gallery(id):
        from app.models import Gallery
        gallery = Gallery.query.get_or_404(id)
        db.session.delete(gallery)
        db.session.commit()
        flash('Foto berhasil dihapus', 'success')
        return redirect(url_for('admin_gallery'))

    # ===== INFO DESA =====
    @app.route('/admin/village')
    @login_required
    def admin_village():
        from app.models import VillageInfo
        infos = VillageInfo.query.all()
        return render_template('admin/village_info.html', infos=infos)

    @app.route('/admin/village/edit/<int:id>', methods=['POST'])
    @login_required
    def admin_edit_village(id):
        from app.models import VillageInfo
        from app.utils.helpers import Helpers
        from flask import current_app
        
        info = VillageInfo.query.get_or_404(id)
        
        title = request.form.get('title')
        content = request.form.get('content')
        is_active = request.form.get('is_active') == 'on'
        
        if not title or not content:
            flash('Judul dan konten wajib diisi', 'danger')
            return redirect(url_for('admin_village'))
        
        info.title = title
        info.content = content
        info.is_active = is_active
        
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename:
            if Helpers.allowed_file(photo_file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                photo_path = Helpers.save_uploaded_file(photo_file, current_app.config['UPLOAD_FOLDER'], 'gallery')
                info.photo_path = photo_path
        
        db.session.commit()
        flash('Informasi desa berhasil diupdate!', 'success')
        return redirect(url_for('admin_village'))

    # =========================================================
    # BLUEPRINT LAINNYA
    # =========================================================
    from app.routes.public import public_bp
    app.register_blueprint(public_bp)
    
    from app.routes.places import places_bp
    app.register_blueprint(places_bp)
    
    from app.routes.ulos import ulos_bp
    app.register_blueprint(ulos_bp)
    
    from app.routes.reviews import reviews_bp
    app.register_blueprint(reviews_bp)
    
    with app.app_context():
        create_folders(app)
    
    return app

def create_folders(app):
    folders = [
        os.path.join(app.config['UPLOAD_FOLDER'], 'places'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'ulos'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'gallery'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'audio'),
        app.config['QR_CODE_FOLDER']
    ]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")