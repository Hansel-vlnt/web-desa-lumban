import os
import re
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

class Helpers:
    @staticmethod
    def allowed_file(filename, allowed_extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    @staticmethod
    def save_uploaded_file(file, upload_folder, subfolder=''):
        if not file or file.filename == '':
            return None
        
        # ===== GUNAKAN UUID UNTUK NAMA FILE =====
        # Ambil ekstensi file
        ext = os.path.splitext(file.filename)[1].lower()  # .jpg, .png, .mp4, dll
        
        # Buat nama file dengan UUID (panjang selalu 36 karakter + ekstensi)
        # Contoh: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6.jpg
        nama_file_baru = f"{uuid.uuid4().hex}{ext}"
        # ========================================
        
        save_path = os.path.join(upload_folder, subfolder)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            print(f"📁 Folder dibuat: {save_path}")
        
        filepath = os.path.join(save_path, nama_file_baru)
        file.save(filepath)
        
        print(f"✅ File saved to: {filepath}")
        
        return f"/static/uploads/{subfolder}/{nama_file_baru}" if subfolder else f"/static/uploads/{nama_file_baru}"
    
    @staticmethod
    def generate_slug(text):
        if not text:
            return ''
        slug = text.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = re.sub(r'^-+|-+$', '', slug)
        return slug
    
    @staticmethod
    def get_audio_mime_type(filename):
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
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
            'mid': 'audio/midi',
            'midi': 'audio/midi',
        }
        return mime_types.get(ext, 'audio/mpeg')
    
    @staticmethod
    def get_audio_extension(filename):
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    @staticmethod
    def is_video_file(filename):
        video_extensions = {'mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv', '3gp', 'mpeg'}
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return ext in video_extensions
    
    @staticmethod
    def get_file_extension(filename):
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''