from flask import Blueprint, render_template, send_file, jsonify, current_app
from app.models import Ulos, UlosPhoto
from app.utils.qr_generator import QRGenerator
from app.utils.helpers import Helpers
import os

ulos_bp = Blueprint('ulos', __name__)

@ulos_bp.route('/ulos')
def ulos_gallery():
    ulos_list = Ulos.query.filter_by(is_active=True).order_by(Ulos.created_at.desc()).all()
    return render_template('public/ulos_gallery.html', ulos_list=ulos_list)

@ulos_bp.route('/ulos/<string:qr_code>')
def ulos_detail_by_qr(qr_code):
    ulos = Ulos.query.filter_by(qr_code=qr_code, is_active=True).first_or_404()
    photos = UlosPhoto.query.filter_by(ulos_id=ulos.id).order_by(UlosPhoto.sort_order).all()
    
    return render_template('public/ulos_detail.html', ulos=ulos, photos=photos)

@ulos_bp.route('/ulos/audio/<int:ulos_id>/<string:language>')
def play_audio(ulos_id, language):
    """Stream audio narasi dengan 3 bahasa"""
    ulos = Ulos.query.get_or_404(ulos_id)
    
    # ===== PILIH AUDIO BERDASARKAN BAHASA =====
    if language == 'id':
        audio_path_str = ulos.audio_indonesia
    elif language == 'en':
        audio_path_str = ulos.audio_english
    elif language == 'batak':
        audio_path_str = ulos.audio_batak
    else:
        return jsonify({'error': 'Bahasa tidak tersedia'}), 404
    # ==========================================
    
    if not audio_path_str:
        return jsonify({'error': 'Audio tidak tersedia untuk bahasa ini'}), 404
    
    # Dapatkan path lengkap file
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filename = os.path.basename(audio_path_str)
    full_path = os.path.join(upload_folder, 'audio', filename)
    
    if not os.path.exists(full_path):
        return jsonify({'error': 'File audio tidak ditemukan'}), 404
    
    # Tentukan MIME type
    ext = Helpers.get_audio_extension(filename)
    mime_types = {
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'm4a': 'audio/mp4',
        'ogg': 'audio/ogg',
        'mp4': 'audio/mp4',
        'aac': 'audio/aac',
        'flac': 'audio/flac',
        'aiff': 'audio/aiff',
        'alac': 'audio/alac',
        'amr': 'audio/amr',
        'opus': 'audio/opus',
        'webm': 'audio/webm',
        '3gp': 'audio/3gpp',
        'mpeg': 'audio/mpeg',
        'jfif': 'audio/mpeg',
        'wma': 'audio/x-ms-wma',
    }
    mime_type = mime_types.get(ext, 'audio/mpeg')
    
    return send_file(full_path, mimetype=mime_type, as_attachment=False)