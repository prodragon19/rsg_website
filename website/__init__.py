# __init__.py (CORRECTED)
import flask  # Optional but keeps your original import
from flask import Flask
from .views import views
from .auth import auth

def create_app():
    app = Flask(__name__)
    
    # ���������� CORRECTED: Set secret key properly (required for sessions)
    app.secret_key = 'NEde R Land'  # ← Use app.secret_key, not config
    
    # ���������� REGISTER BLUEPRINTS (fix indentation!)
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    return app  # ← Must be indented under create_app()
