from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from app.models import Gallery
from app.utils.helpers import Helpers
from app import db
from app.routes.admin import admin_bp
import os

@admin_bp.route('/gallery')
@login_required
def admin_gallery():
    images = Gallery.query.order_by(Gallery.created_at.desc()).all()
    return render_template('admin/gallery.html', images=images)

@admin_bp.route('/gallery/add', methods=['POST'])
@login_required
def admin_add_gallery():
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

@admin_bp.route('/gallery/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_gallery(id):
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

@admin_bp.route('/gallery/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_gallery(id):
    gallery = Gallery.query.get_or_404(id)
    
    # Hapus file fisik
    old_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'],
        gallery.photo_path.replace('/static/uploads/', '')
    )
    if os.path.exists(old_path):
        os.remove(old_path)
    
    db.session.delete(gallery)
    db.session.commit()
    flash('Foto berhasil dihapus', 'success')
    return redirect(url_for('admin_gallery'))