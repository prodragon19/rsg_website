from website import create_app, db
from website.models import AdminUser
from website.extensions import bcrypt


app = create_app()

with app.app_context():

    password = bcrypt.generate_password_hash(
        "1234"
    ).decode("utf-8")


    admin = AdminUser(
        username="admin",
        email="admin@rsgsoftware.com",
        password_hash=password,
        role="Owner",
        enabled=True
    )


    db.session.add(admin)
    db.session.commit()


    print("Admin created")