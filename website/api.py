import os
import secrets

from flask import Blueprint, jsonify, request
from functools import wraps

from . import db
from .extensions import bcrypt, limiter
from .models import Customer, Order

api = Blueprint("api", __name__, url_prefix="/api")

PRODUCTS = [
    {
        "id": "seabee",
        "name": "Republic RC-3 Seabee",
        "simulator": "MSFS 2024",
        "version": "0.1.0-dev",
        "folder_name": "rsg-seabee",
        "download_url": os.getenv("SEABEE_DOWNLOAD_URL", ""),
        "status": "in_development",
    }
]


def get_customer_from_token():
    header = request.headers.get("Authorization", "")
    token = header.replace("Bearer ", "").strip()
    if not token:
        return None
    return Customer.query.filter_by(api_token=token).first()


def require_customer(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        customer = get_customer_from_token()
        if not customer or customer.banned:
            return jsonify({"error": "Unauthorized"}), 401
        return fn(customer, *args, **kwargs)
    return wrapper


@api.route("/login", methods=["POST"])
@limiter.limit("8 per minute")
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    customer = Customer.query.filter_by(email=email).first()
    if (
        not customer
        or customer.banned
        or not customer.password_hash
        or not bcrypt.check_password_hash(customer.password_hash, password)
    ):
        return jsonify({"error": "Invalid email or password"}), 401

    if not customer.api_token:
        customer.api_token = secrets.token_urlsafe(32)
        db.session.commit()

    return jsonify({
        "token": customer.api_token,
        "name": customer.name,
        "email": customer.email,
    })


@api.route("/me")
@require_customer
def api_me(customer):
    return jsonify({
        "name": customer.name,
        "email": customer.email,
    })


def customer_owns_product(customer, product_id):
    if os.getenv("RSG_DEV_UNLOCK", "").lower() == "true":
        return True

    paid = Order.query.filter_by(
        customer_id=customer.id,
        payment_status="Paid",
    ).count()
    return paid > 0 and product_id == "seabee"


@api.route("/products")
@require_customer
def api_products(customer):
    items = []
    for product in PRODUCTS:
        item = dict(product)
        item["owned"] = customer_owns_product(customer, product["id"])
        if not item["owned"]:
            item["download_url"] = ""
        items.append(item)
    return jsonify({"products": items})