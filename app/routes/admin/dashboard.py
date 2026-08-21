from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash
from app.models import Admin, Place, Ulos, Review, Category, Gallery
from app import db
from app.routes.admin import admin_bp

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            admin.last_login = db.func.now()
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username atau password salah', 'danger')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Anda telah logout', 'info')
    return redirect(url_for('admin_login'))

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
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