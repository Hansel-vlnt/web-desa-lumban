from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from app.models import VillageInfo
from app.utils.helpers import Helpers
from app import db
from app.routes.admin import admin_bp
import os

@admin_bp.route('/village')
@login_required
def village_info():
    infos = VillageInfo.query.all()
    return render_template('admin/village_info.html', infos=infos)

@admin_bp.route('/village/edit/<int:id>', methods=['POST'])
@login_required
def edit_village_info(id):
    info = VillageInfo.query.get_or_404(id)
    
    title = request.form.get('title')
    content = request.form.get('content')
    is_active = request.form.get('is_active') == 'on'
    
    if not title or not content:
        flash('Judul dan konten wajib diisi', 'danger')
        return redirect(url_for('admin.village_info'))
    
    info.title = title
    info.content = content
    info.is_active = is_active
    
    # Handle photo upload
    photo_file = request.files.get('photo')
    if photo_file and photo_file.filename:
        if Helpers.allowed_file(photo_file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            # Hapus foto lama
            if info.photo_path:
                old_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    info.photo_path.replace('/static/uploads/', '')
                )
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            photo_path = Helpers.save_uploaded_file(
                photo_file,
                current_app.config['UPLOAD_FOLDER'],
                'gallery'
            )
            info.photo_path = photo_path
        else:
            flash('Format file tidak didukung', 'danger')
            return redirect(url_for('admin.village_info'))
    
    db.session.commit()
    flash('Informasi desa berhasil diupdate!', 'success')
    return redirect(url_for('admin.village_info'))