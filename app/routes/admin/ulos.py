from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from app.models import Ulos, UlosPhoto
from app.utils.helpers import Helpers
from app.utils.qr_generator import QRGenerator
from app import db
from app.routes.admin import admin_bp
import os
from datetime import datetime


# ===== LIST ULOS =====
@admin_bp.route('/ulos')
@login_required
def admin_ulos():
    ulos_list = Ulos.query.order_by(Ulos.created_at.desc()).all()
    return render_template('admin/ulos_list.html', ulos_list=ulos_list)


# ===== ADD ULOS =====
@admin_bp.route('/ulos/add', methods=['GET', 'POST'])
@login_required
def admin_add_ulos():
    if request.method == 'POST':
        name = request.form.get('name')
        motif_description_text = request.form.get('motif_description_text', '')
        meaning_text = request.form.get('meaning_text', '')
        function_text = request.form.get('function_text', '')
        
        print("="*60)
        print(f"📝 MENAMBAH ULOS: {name}")
        print(f"📝 motif_description_text: {motif_description_text[:100] if motif_description_text else 'KOSONG!'}")
        print("="*60)
        
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
        
        # Upload Audio
        audio_id = request.files.get('audio_id')
        if audio_id and audio_id.filename:
            if Helpers.allowed_file(audio_id.filename, current_app.config['ALLOWED_AUDIO_EXTENSIONS']):
                audio_path = Helpers.save_uploaded_file(audio_id, current_app.config['UPLOAD_FOLDER'], 'audio')
                ulos.audio_indonesia = audio_path
        
        audio_en = request.files.get('audio_en')
        if audio_en and audio_en.filename:
            if Helpers.allowed_file(audio_en.filename, current_app.config['ALLOWED_AUDIO_EXTENSIONS']):
                audio_path = Helpers.save_uploaded_file(audio_en, current_app.config['UPLOAD_FOLDER'], 'audio')
                ulos.audio_english = audio_path
        
        audio_batak = request.files.get('audio_batak')
        if audio_batak and audio_batak.filename:
            if Helpers.allowed_file(audio_batak.filename, current_app.config['ALLOWED_AUDIO_EXTENSIONS']):
                audio_path = Helpers.save_uploaded_file(audio_batak, current_app.config['UPLOAD_FOLDER'], 'audio')
                ulos.audio_batak = audio_path
        
        db.session.commit()
        QRGenerator.generate_ulos_qr(ulos.id, ulos.name, ulos.qr_code)
        
        saved = Ulos.query.get(ulos.id)
        print(f"✅ SETELAH SAVE: motif_description_text = {saved.motif_description_text[:50] if saved.motif_description_text else 'KOSONG!'}")
        
        flash(f'ULOS berhasil ditambahkan! QR Code: {ulos.qr_code}', 'success')
        return redirect(url_for('admin_ulos'))
    
    return render_template('admin/ulos_form.html')


# ===== EDIT ULOS =====
@admin_bp.route('/ulos/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_ulos(id):
    ulos = Ulos.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        motif_description_text = request.form.get('motif_description_text', '')
        meaning_text = request.form.get('meaning_text', '')
        function_text = request.form.get('function_text', '')
        is_active = request.form.get('is_active') == 'on'
        
        print("="*60)
        print(f"📝 UPDATE ULOS ID {id}: {name}")
        print(f"📝 motif_description_text: {motif_description_text[:100] if motif_description_text else 'KOSONG!'}")
        print("="*60)
        
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
        ulos.updated_at = datetime.utcnow()
        
        # ===== FOTO =====
        photos = request.files.getlist('photos')
        photos = [f for f in photos if f and f.filename]
        
        if photos:
            last_order = UlosPhoto.query.filter_by(ulos_id=ulos.id).order_by(UlosPhoto.sort_order.desc()).first()
            start_order = (last_order.sort_order + 1) if last_order else 0
            
            for idx, photo in enumerate(photos):
                if Helpers.allowed_file(photo.filename, current_app.config['ALLOWED_EXTENSIONS']):
                    photo_path = Helpers.save_uploaded_file(photo, current_app.config['UPLOAD_FOLDER'], 'ulos')
                    ulos_photo = UlosPhoto(
                        ulos_id=ulos.id,
                        photo_path=photo_path,
                        is_primary=(len(ulos.photos) == 0 and idx == 0),
                        sort_order=start_order + idx
                    )
                    db.session.add(ulos_photo)
        
        # ===== HAPUS FOTO =====
        remove_photo_ids = request.form.getlist('remove_photos')
        if remove_photo_ids:
            for photo_id in remove_photo_ids:
                photo = UlosPhoto.query.get(int(photo_id))
                if photo and photo.ulos_id == ulos.id:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.photo_path.replace('/static/uploads/', ''))
                    if os.path.exists(old_path):
                        os.remove(old_path)
                    db.session.delete(photo)
        
        # ===== AUDIO =====
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
        
        db.session.commit()
        
        saved = Ulos.query.get(ulos.id)
        print(f"✅ SETELAH SAVE: motif_description_text = {saved.motif_description_text[:50] if saved.motif_description_text else 'KOSONG!'}")
        
        flash('ULOS berhasil diupdate!', 'success')
        return redirect(url_for('admin_ulos'))
    
    return render_template('admin/ulos_form.html', ulos=ulos)


# ===== DELETE ULOS =====
@admin_bp.route('/ulos/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_ulos(id):
    ulos = Ulos.query.get_or_404(id)
    db.session.delete(ulos)
    db.session.commit()
    flash('ULOS berhasil dihapus', 'success')
    return redirect(url_for('admin_ulos'))


# ===== DELETE ULOS PHOTO =====
@admin_bp.route('/ulos/photo/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_ulos_photo(id):
    photo = UlosPhoto.query.get_or_404(id)
    ulos_id = photo.ulos_id
    db.session.delete(photo)
    db.session.commit()
    flash('Foto berhasil dihapus', 'success')
    return redirect(url_for('admin_edit_ulos', id=ulos_id))