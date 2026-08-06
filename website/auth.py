# website/auth.py

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from datetime import datetime

from user_agents import parse

from . import db

from .models import (
    AdminUser,
    AdminSession,
    AuditLog
)

from .extensions import bcrypt



auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)





def create_audit(action, target=None):

    log = AuditLog(
        admin_id=session.get("admin_id"),
        action=action,
        target=target,
        ip_address=request.remote_addr
    )

    db.session.add(log)





def create_device_session(admin):

    user_agent = request.headers.get(
        "User-Agent"
    )


    parsed = parse(user_agent)


    device = AdminSession(

        admin_id=admin.id,

        ip_address=request.remote_addr,

        browser=parsed.browser.family,

        operating_system=parsed.os.family,

        device_type=parsed.device.family

    )


    db.session.add(device)






@auth.route(
    "/login",
    methods=["GET", "POST"]
)
def login():


    if request.method == "POST":


        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )



        admin = AdminUser.query.filter_by(
            username=username
        ).first()



        if not admin:


            flash(
                "Invalid username or password",
                "danger"
            )


            return redirect(
                url_for("auth.login")
            )





        if not admin.enabled:


            flash(
                "Account disabled",
                "danger"
            )


            return redirect(
                url_for("auth.login")
            )





        if bcrypt.check_password_hash(
            admin.password_hash,
            password
        ):



            session["logged_in"] = True

            session["admin_id"] = admin.id

            session["username"] = admin.username

            session["role"] = admin.role



            admin.last_login = datetime.utcnow()



            create_device_session(
                admin
            )


            create_audit(
                "Admin logged in",
                admin.username
            )



            db.session.commit()



            return redirect(
                url_for(
                    "admin.dashboard"
                )
            )




        flash(
            "Invalid username or password",
            "danger"
        )



    return render_template(
        "admin/login.html"
    )








@auth.route("/logout")
def logout():


    if session.get(
        "admin_id"
    ):


        create_audit(
            "Admin logged out",
            session.get("username")
        )


        db.session.commit()



    session.clear()



    return redirect(
        url_for(
            "views.home"
        )
    )