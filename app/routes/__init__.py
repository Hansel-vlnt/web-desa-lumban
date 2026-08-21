from flask import Blueprint

# Buat blueprint admin
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import semua route
from app.routes.admin import dashboard
from app.routes.admin import categories
from app.routes.admin import places
from app.routes.admin import ulos
from app.routes.admin import gallery
from app.routes.admin import village