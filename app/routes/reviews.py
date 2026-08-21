from flask import Blueprint, request, jsonify, session
from app.models import Review
from app import db
import random
import hashlib
from datetime import datetime

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/review/submit', methods=['POST'])
def submit_review():
    place_id = request.form.get('place_id')
    reviewer_name = request.form.get('name')
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    
    if not all([place_id, reviewer_name, rating]):
        return jsonify({'error': 'Data tidak lengkap'}), 400
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating harus 1-5'}), 400
    except ValueError:
        return jsonify({'error': 'Rating tidak valid'}), 400
    
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()
    
    review = Review(
        place_id=place_id,
        reviewer_name=reviewer_name,
        rating=rating,
        comment=comment,
        otp_code=otp_hash,
        is_verified=False,
        ip_address=request.remote_addr
    )
    
    db.session.add(review)
    db.session.commit()
    
    session['review_id'] = review.id
    session['otp'] = otp
    
    return jsonify({
        'success': True,
        'review_id': review.id,
        'otp': otp,
        'message': 'Review berhasil disimpan'
    })

@reviews_bp.route('/review/verify', methods=['POST'])
def verify_review():
    review_id = request.form.get('review_id')
    otp_input = request.form.get('otp')
    
    if not review_id or not otp_input:
        return jsonify({'error': 'Data tidak lengkap'}), 400
    
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'error': 'Review tidak ditemukan'}), 404
    
    if review.is_verified:
        return jsonify({'error': 'Review sudah diverifikasi'}), 400
    
    otp_hash = hashlib.sha256(otp_input.encode()).hexdigest()
    
    if otp_hash == review.otp_code:
        review.is_verified = True
        review.verified_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Review berhasil diverifikasi!'})
    else:
        return jsonify({'error': 'OTP tidak valid'}), 400