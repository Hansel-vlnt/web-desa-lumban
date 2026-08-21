from app import create_app, db
from werkzeug.security import generate_password_hash
from app.models import Admin

app = create_app()

with app.app_context():
    print("🔄 Creating database tables...")
    db.create_all()
    print("✅ Tables created!")
    
    # Create admin user
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(
            username='admin',
            email='admin@kampungulos.com',
            password_hash=generate_password_hash('password123'),
            full_name='Administrator Desa',
            role='super_admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created!")
    
    print("\n" + "="*50)
    print("🎉 Database Ready!")
    print("="*50)
    print("\n📊 Database MySQL:")
    print("   Database: Dewi_LuSi")
    print("   Server: localhost")
    print("   phpMyAdmin: http://localhost/phpmyadmin")
    print("\n🔑 Login Admin:")
    print("   Username: admin")
    print("   Password: password123")
    print("\n🌐 Website:")
    print("   http://localhost:5000")
    print("   http://localhost:5000/admin")
    print("="*50)