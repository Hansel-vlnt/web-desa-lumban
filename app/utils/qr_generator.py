import qrcode
from PIL import Image
import os
import hashlib
import time
from flask import url_for

class QRGenerator:
    @staticmethod
    def generate_unique_code(ulos_name):
        raw = f"{ulos_name}-{int(time.time())}"
        hash_obj = hashlib.md5(raw.encode())
        return f"ULOS-{hash_obj.hexdigest()[:8].upper()}"
    
    @staticmethod
    def create_qr_with_logo(data, logo_path=None, size=300):
        qr = qrcode.QRCode(
            version=3,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="#1a5276", back_color="white").convert('RGB')
        
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path)
                qr_width, qr_height = qr_img.size
                logo_size = int(qr_width * 0.2)
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                qr_img.paste(logo, pos, logo if logo.mode == 'RGBA' else None)
            except Exception as e:
                print(f"Error adding logo: {e}")
        
        return qr_img
    
    @staticmethod
    def save_qr(qr_img, ulos_id, output_dir=None):
        if output_dir is None:
            from app import create_app
            app = create_app()
            output_dir = app.config['QR_CODE_FOLDER']
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filename = f"ulos_{ulos_id}.png"
        filepath = os.path.join(output_dir, filename)
        qr_img.save(filepath, quality=95)
        return f"/static/qr_codes/{filename}"
    
    @staticmethod
    def generate_ulos_qr(ulos_id, ulos_name, qr_code):
        from flask import url_for
        url = url_for('ulos.ulos_detail_by_qr', qr_code=qr_code, _external=True)
        qr_img = QRGenerator.create_qr_with_logo(url)
        return QRGenerator.save_qr(qr_img, ulos_id)