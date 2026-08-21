from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Place, Category, PlacePhoto
from app.utils.helpers import Helpers
from app import db
from app.routes.admin import admin_bp
import os
from datetime import datetime


# ===== LIST PLACES =====
@admin_bp.route('/places')
@login_required
def admin_places():
    places = Place.query.order_by(Place.created_at.desc()).all()
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('admin/places.html', places=places, categories=categories)


# ===== ADD PLACE =====
@admin_bp.route('/places/add', methods=['GET', 'POST'])
@login_required
def admin_add_place():
    categories = Category.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id')
        description_text = request.form.get('description_text', '')
        address = request.form.get('address', '')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        google_maps_url = request.form.get('google_maps_url', '')
        whatsapp_number = request.form.get('whatsapp_number', '')
        opening_hours = request.form.get('opening_hours', '')
        destination_group = request.form.get('destination_group', 'umum')
        place_type = request.form.get('place_type', 'wisata')
        
        print("="*60)
        print(f"📝 MENAMBAH TEMPAT WISATA: {name}")
        print(f"📝 description_text: {description_text[:100] if description_text else 'KOSONG!'}")
        print("="*60)
        
        if not name or not category_id:
            flash('Nama dan kategori wajib diisi', 'danger')
            return redirect(url_for('admin_add_place'))
        
        # Foto utama
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
            created_by=current_user.id
        )
        
        db.session.add(place)
        db.session.commit()
        
        # Slide photos
        slide_photos = request.files.getlist('slide_photos')
        for idx, photo in enumerate(slide_photos):
            if photo and photo.filename:
                if Helpers.allowed_file(photo.filename, current_app.config['ALLOWED_EXTENSIONS']):
                    photo_path = Helpers.save_uploaded_file(photo, current_app.config['UPLOAD_FOLDER'], 'places')
                    place_photo = PlacePhoto(
                        place_id=place.id,
                        photo_path=photo_path,
                        is_primary=(idx == 0),
                        is_video=False,
                        sort_order=idx
                    )
                    db.session.add(place_photo)
        db.session.commit()
        
        saved = Place.query.get(place.id)
        print(f"✅ SETELAH SAVE: description_text = {saved.description_text[:50] if saved.description_text else 'KOSONG!'}")
        
        flash('Tempat wisata berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_places'))
    
    return render_template('admin/place_form.html', categories=categories)


# ===== EDIT PLACE =====
@admin_bp.route('/places/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_place(id):
    place = Place.query.get_or_404(id)
    categories = Category.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id')
        description_text = request.form.get('description_text', '')
        address = request.form.get('address', '')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        google_maps_url = request.form.get('google_maps_url', '')
        whatsapp_number = request.form.get('whatsapp_number', '')
        opening_hours = request.form.get('opening_hours', '')
        destination_group = request.form.get('destination_group', 'umum')
        is_active = request.form.get('is_active') == 'on'
        
        print("="*60)
        print(f"📝 UPDATE TEMPAT WISATA ID {id}: {name}")
        print(f"📝 description_text: {description_text[:100] if description_text else 'KOSONG!'}")
        print("="*60)
        
        if not name or not category_id:
            flash('Nama dan kategori wajib diisi', 'danger')
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
        place.is_active = is_active
        place.updated_at = datetime.utcnow()
        
        # ===== FOTO UTAMA =====
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename:
            if Helpers.allowed_file(photo_file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                if place.photo_path:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], place.photo_path.replace('/static/uploads/', ''))
                    if os.path.exists(old_path):
                        os.remove(old_path)
                photo_path = Helpers.save_uploaded_file(photo_file, current_app.config['UPLOAD_FOLDER'], 'places')
                place.photo_path = photo_path
            else:
                flash('Format file foto tidak didukung', 'danger')
                return redirect(url_for('admin_edit_place', id=id))
        
        # ===== FOTO SLIDE =====
        slide_photos = request.files.getlist('slide_photos')
        slide_photos = [f for f in slide_photos if f and f.filename]
        
        if slide_photos:
            last_order = PlacePhoto.query.filter_by(place_id=place.id).order_by(PlacePhoto.sort_order.desc()).first()
            start_order = (last_order.sort_order + 1) if last_order else 0
            
            for idx, photo in enumerate(slide_photos):
                if Helpers.allowed_file(photo.filename, current_app.config['ALLOWED_EXTENSIONS']):
                    photo_path = Helpers.save_uploaded_file(photo, current_app.config['UPLOAD_FOLDER'], 'places')
                    place_photo = PlacePhoto(
                        place_id=place.id,
                        photo_path=photo_path,
                        is_primary=False,
                        is_video=False,
                        sort_order=start_order + idx
                    )
                    db.session.add(place_photo)
        
        # ===== HAPUS FOTO SLIDE =====
        remove_photo_ids = request.form.getlist('remove_photos')
        if remove_photo_ids:
            for photo_id in remove_photo_ids:
                photo = PlacePhoto.query.get(int(photo_id))
                if photo and photo.place_id == place.id:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.photo_path.replace('/static/uploads/', ''))
                    if os.path.exists(old_path):
                        os.remove(old_path)
                    db.session.delete(photo)
        
        db.session.commit()
        
        saved = Place.query.get(place.id)
        print(f"✅ SETELAH SAVE: description_text = {saved.description_text[:50] if saved.description_text else 'KOSONG!'}")
        
        flash('Tempat wisata berhasil diupdate!', 'success')
        return redirect(url_for('admin_places'))
    
    all_photos = place.photos.order_by(PlacePhoto.sort_order).all()
    return render_template('admin/place_form.html', place=place, categories=categories, all_photos=all_photos)


# ===== DELETE PLACE =====
@admin_bp.route('/places/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_place(id):
    place = Place.query.get_or_404(id)
    
    for photo in place.photos:
        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.photo_path.replace('/static/uploads/', ''))
        if os.path.exists(old_path):
            os.remove(old_path)
    
    if place.photo_path:
        old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], place.photo_path.replace('/static/uploads/', ''))
        if os.path.exists(old_path):
            os.remove(old_path)
    
    db.session.delete(place)
    db.session.commit()
    
    flash('Tempat wisata berhasil dihapus', 'success')
    return redirect(url_for('admin_places'))


# ===== DELETE PLACE PHOTO =====
@admin_bp.route('/places/photo/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_place_photo(id):
    photo = PlacePhoto.query.get_or_404(id)
    place_id = photo.place_id
    
    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.photo_path.replace('/static/uploads/', ''))
    if os.path.exists(old_path):
        os.remove(old_path)
    
    db.session.delete(photo)
    db.session.commit()
    
    flash('File berhasil dihapus!', 'success')
    return redirect(url_for('admin_edit_place', id=place_id))