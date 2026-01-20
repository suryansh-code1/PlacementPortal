from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os




db = SQLAlchemy()
login_manager = LoginManager()




def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'placement-portal-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    
    from .controllers import auth_bp, admin_bp, company_bp, student_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)
    
    return app
