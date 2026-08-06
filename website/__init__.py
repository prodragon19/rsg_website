# website/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # ← DEFINED FIRST (avoids circular imports)

def create_app():
    app = Flask(__name__)
    import os  # ← ONLY IMPORT NEEDED
    
    # ������������������������ PURE ENV VARS (WORKS EVERYWHERE)
    app.secret_key = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///app.db'  # Fallback for local dev
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # ������������������������ NOW SAFE TO IMPORT BLUEPRINTS
    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    with app.app_context():
        db.create_all()
    
    return app
