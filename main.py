from application import create_app, db
from application.models import User




app = create_app()




def init_db():
    with app.app_context():
        db.create_all()
        
        admin = User.query.filter_by(email='admin@portal.com').first()
        if not admin:
            admin = User(
                email='admin@portal.com',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created: admin@portal.com / admin123')
        else:
            print('Admin user already exists.')




if __name__ == '__main__':
    init_db()
    app.run(debug=True)
