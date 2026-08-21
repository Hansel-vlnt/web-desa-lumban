from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Category
from app.utils.helpers import Helpers
from app import db
from app.routes.admin import admin_bp

@admin_bp.route('/categories')
@login_required
def categories_list():
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name', '').strip()
    icon = request.form.get('icon', 'fa-tag')
    description = request.form.get('description', '')
    
    if not name:
        flash('Nama kategori wajib diisi', 'danger')
        return redirect(url_for('admin.categories_list'))
    
    existing = Category.query.filter_by(name=name).first()
    if existing:
        flash('Kategori sudah ada', 'warning')
        return redirect(url_for('admin.categories_list'))
    
    category = Category(
        name=name,
        slug=Helpers.generate_slug(name),
        icon=icon,
        description=description,
        is_active=True
    )
    
    db.session.add(category)
    db.session.commit()
    flash('Kategori berhasil ditambahkan', 'success')
    return redirect(url_for('admin.categories_list'))

@admin_bp.route('/categories/edit/<int:id>', methods=['POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    
    name = request.form.get('name', '').strip()
    icon = request.form.get('icon', category.icon)
    description = request.form.get('description', category.description)
    is_active = request.form.get('is_active') == 'on'
    
    if not name:
        flash('Nama kategori wajib diisi', 'danger')
        return redirect(url_for('admin.categories_list'))
    
    existing = Category.query.filter(
        Category.name == name,
        Category.id != id
    ).first()
    
    if existing:
        flash('Nama kategori sudah digunakan oleh data lain!', 'warning')
        return redirect(url_for('admin.categories_list'))
    
    category.name = name
    category.slug = Helpers.generate_slug(name)
    category.icon = icon
    category.description = description
    category.is_active = is_active
    
    db.session.commit()
    flash('Kategori berhasil diupdate', 'success')
    return redirect(url_for('admin.categories_list'))

@admin_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    if category.places:
        flash('Kategori tidak bisa dihapus karena masih memiliki tempat wisata', 'danger')
        return redirect(url_for('admin.categories_list'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Kategori berhasil dihapus', 'success')
    return redirect(url_for('admin.categories_list'))