"""Separate public customer authentication from privileged admin access."""
from .email import send_welcome_email
from datetime import datetime

import pyotp
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from user_agents import parse

from . import db
from .extensions import bcrypt, limiter
from .models import AdminSession, AdminUser, AuditLog, Customer

auth = Blueprint("auth", __name__)


def create_audit(action, target=None):
    db.session.add(AuditLog(
        admin_id=session.get("admin_id"), action=action, target=target,
        ip_address=request.remote_addr,
    ))


def create_device_session(admin):
    parsed = parse(request.headers.get("User-Agent", ""))
    country = request.headers.get("CF-IPCountry") or request.headers.get("X-Country")
    previous_ips = {item.ip_address for item in AdminSession.query.filter_by(admin_id=admin.id).all()}
    unusual = bool(previous_ips and request.remote_addr not in previous_ips)
    device = AdminSession(
        admin_id=admin.id, ip_address=request.remote_addr, country=country,
        browser=parsed.browser.family, operating_system=parsed.os.family,
        device_type=parsed.device.family, unusual=unusual,
    )
    db.session.add(device)
    return device


def start_admin_session(admin):
    device = create_device_session(admin)
    db.session.flush()
    session.clear()
    session.update({
        "logged_in": True, "admin_id": admin.id, "username": admin.username,
        "role": admin.role, "device_session_id": device.id,
    })
    admin.last_login = datetime.utcnow()
    create_audit("Admin logged in", admin.username)
    db.session.commit()


@auth.route("/admin/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = AdminUser.query.filter_by(username=username).first()
        if not admin or not admin.enabled or not bcrypt.check_password_hash(admin.password_hash, password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("auth.admin_login"))
        if admin.two_factor_enabled:
            session.clear()
            session["pending_admin_id"] = admin.id
            return redirect(url_for("auth.verify_two_factor"))
        start_admin_session(admin)
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/login.html")


@auth.route("/admin/verify-2fa", methods=["GET", "POST"])
@limiter.limit("8 per minute", methods=["POST"])
def verify_two_factor():
    admin_id = session.get("pending_admin_id")
    admin = db.session.get(AdminUser, admin_id) if admin_id else None
    if not admin:
        return redirect(url_for("auth.admin_login"))
    if request.method == "POST":
        code = request.form.get("code", "").replace(" ", "")
        if admin.two_factor_secret and pyotp.TOTP(admin.two_factor_secret).verify(code, valid_window=1):
            start_admin_session(admin)
            return redirect(url_for("admin.dashboard"))
        flash("Invalid authentication code.", "danger")
    return render_template("admin/verify_2fa.html")


@auth.route("/admin/logout", methods=["POST"])
def logout():
    device_id = session.get("device_session_id")
    device = db.session.get(AdminSession, device_id) if device_id else None
    if device:
        device.active = False
        create_audit("Admin logged out", session.get("username"))
        db.session.commit()
    session.clear()
    return redirect(url_for("views.home"))


@auth.route("/signup", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def signup():
    """Public signup creates a customer account only—never an administrator."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter a name, email, and a password of at least 8 characters.", "danger")
        elif Customer.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
        else:
            customer = Customer(name=name, email=email, password_hash=bcrypt.generate_password_hash(password).decode("utf-8"))
            db.session.add(customer)
            db.session.commit()
            session.clear()
            session.update({"customer_id": customer.id, "customer_name": customer.name})
            flash("Your account has been created.", "success")
            return redirect(url_for("views.home"))
    return render_template("signup.html")


@auth.route("/login", methods=["GET", "POST"], endpoint="login")
@limiter.limit("5 per minute", methods=["POST"])
def customer_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        customer = Customer.query.filter_by(email=email).first()
        if not customer or customer.banned or not customer.password_hash or not bcrypt.check_password_hash(customer.password_hash, password):
            flash("Invalid email or password.", "danger")
        else:
            customer.last_login = datetime.utcnow()
            db.session.commit()
            session.clear()
            session.update({"customer_id": customer.id, "customer_name": customer.name})
            return redirect(url_for("views.home"))
    return render_template("login.html")


@auth.route("/logout", methods=["POST"])
def customer_logout():
    session.clear()
    return redirect(url_for("views.home"))
