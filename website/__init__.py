from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .extensions import (
    bcrypt,
    login_manager,
    csrf,
    limiter
)

db = SQLAlchemy()


def create_app():

    app = Flask(__name__)


    app.config["SECRET_KEY"] = "CHANGE_THIS_TO_A_RANDOM_SECRET"


    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


    db.init_app(app)

    bcrypt.init_app(app)

    login_manager.init_app(app)

    csrf.init_app(app)

    limiter.init_app(app)


    login_manager.login_view = "auth.login"


    from .views import views
    app.register_blueprint(views)


    from .auth import auth
    app.register_blueprint(auth)


    from .admin import admin
    app.register_blueprint(admin)


    with app.app_context():
        db.create_all()


    return app