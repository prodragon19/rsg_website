# __init__.py - ADD THESE LINES
from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # ← NEW IMPORT
from .views import views
from .auth import auth

db = SQLAlchemy()  # ← NEW: Initialize DB

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'NEde R Land'  # Keep your key (but see security note below)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # ← NEW: SQLite DB
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # ← NEW: Prevents warning
    
    db.init_app(app)  # ← NEW: Connect DB to app
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    return app