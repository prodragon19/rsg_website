from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


bcrypt = Bcrypt()

login_manager = LoginManager()

csrf = CSRFProtect()

limiter = Limiter(
    key_func=get_remote_address
)


@login_manager.user_loader
def load_user(user_id):

    from .models import AdminUser

    return AdminUser.query.get(int(user_id))