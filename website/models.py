# website/models.py

from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Numeric

from . import db



class NewsletterPost(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    author = db.Column(
        db.String(100),
        default="Anonymous"
    )

    image_filename = db.Column(
        db.String(200)
    )

    date_posted = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )


    def __repr__(self):
        return f"<NewsletterPost {self.title}>"




class AdminUser(db.Model, UserMixin):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(200),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        default="Support"
    )

    enabled = db.Column(
        db.Boolean,
        default=True
    )

    two_factor_enabled = db.Column(
        db.Boolean,
        default=False
    )

    two_factor_secret = db.Column(
        db.String(255)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    last_login = db.Column(
        db.DateTime
    )


    sessions = db.relationship(
        "AdminSession",
        backref="admin",
        lazy=True,
        cascade="all, delete"
    )




class AdminSession(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    admin_id = db.Column(
        db.Integer,
        db.ForeignKey("admin_user.id"),
        nullable=False
    )


    ip_address = db.Column(
        db.String(100)
    )


    country = db.Column(
        db.String(100)
    )


    browser = db.Column(
        db.String(100)
    )


    operating_system = db.Column(
        db.String(100)
    )


    device_type = db.Column(
        db.String(100)
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    last_active = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    active = db.Column(
        db.Boolean,
        default=True
    )

    unusual = db.Column(
        db.Boolean,
        default=False
    )




class AuditLog(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    admin_id = db.Column(
        db.Integer,
        db.ForeignKey("admin_user.id")
    )


    action = db.Column(
        db.String(255),
        nullable=False
    )


    target = db.Column(
        db.String(255)
    )


    ip_address = db.Column(
        db.String(100)
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )




class Customer(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    name = db.Column(
        db.String(150),
        nullable=False
    )


    email = db.Column(
        db.String(200),
        unique=True,
        nullable=False
    )


    password_hash = db.Column(
        db.String(255)
    )


    banned = db.Column(
        db.Boolean,
        default=False
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    last_login = db.Column(
        db.DateTime
    )


    orders = db.relationship(
        "Order",
        backref="customer",
        lazy=True,
        cascade="all, delete"
    )


    tickets = db.relationship(
        "SupportTicket",
        backref="customer",
        lazy=True,
        cascade="all, delete"
    )




class Order(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customer.id"),
        nullable=False
    )


    status = db.Column(
        db.String(50),
        default="Pending"
    )


    payment_status = db.Column(
        db.String(50),
        default="Unpaid"
    )


    amount = db.Column(
        Numeric(10,2),
        default=0
    )


    invoice_file = db.Column(
        db.String(255)
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    refunds = db.relationship(
        "Refund",
        backref="order",
        lazy=True,
        cascade="all, delete"
    )




class Refund(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )


    amount = db.Column(
        Numeric(10,2)
    )


    reason = db.Column(
        db.Text
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )




class SupportTicket(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customer.id"),
        nullable=False
    )


    subject = db.Column(
        db.String(200)
    )


    message = db.Column(
        db.Text
    )


    status = db.Column(
        db.String(50),
        default="Open"
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
