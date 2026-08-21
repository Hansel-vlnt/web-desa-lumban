import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    
    # ====== DATABASE ======
    _raw_db_url = os.environ.get('DATABASE_URL') or 'postgresql+psycopg2://postgres.yabmjbtboftihfeedpxk:Hanselgant140205@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres'
    if _raw_db_url.startswith('postgres://'):
        _raw_db_url = _raw_db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
    elif _raw_db_url.startswith('postgresql://') and not _raw_db_url.startswith('postgresql+psycopg2://'):
        _raw_db_url = _raw_db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    
    SQLALCHEMY_DATABASE_URI = _raw_db_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # Upload
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app/static/uploads')
    QR_CODE_FOLDER = os.path.join(BASE_DIR, 'app/static/qr_codes')
    
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB (untuk video)
    
    # ===== FORMAT YANG DIDUKUNG =====
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'jfif', 'bmp', 'svg'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv', '3gp'}
    ALLOWED_AUDIO_EXTENSIONS = {
        'mp3', 'wav', 'm4a', 'ogg', 'mp4', 'aac', 'flac', 'aiff', 'alac',
        'amr', 'awb', 'opus', 'webm', '3gp', '3g2', 'mpeg', 'mpga', 'jfif',
        'wma', 'ra', 'rm', 'mid', 'midi', 'kar'
    }
    
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300