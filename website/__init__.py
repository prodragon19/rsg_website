# website/__init__.py (CORRECTED VERSION)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# ���������������� STEP 1: DEFINE DB FIRST (BEFORE ANY IMPORTS)
db = SQLAlchemy()  # ← THIS MUST COME FIRST

def create_app():
    app = Flask(__name__)
    
    # ���������������� STEP 2: CONFIGURE APP
    import os
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file (create this locally)
    
    app.secret_key = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///app.db'  # Fallback for local dev
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # ���������������� STEP 3: INITIALIZE DB WITH APP
    db.init_app(app)
    
    # ���������������� STEP 4: NOW IMPORT BLUEPRINTS (SAFE TO DO)
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    # ���������������� STEP 5: CREATE TABLES
    with app.app_context():
        db.create_all()
    
    return app
