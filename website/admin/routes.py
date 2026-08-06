# website/admin/routes.py

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from datetime import datetime

from . import admin

from .decorators import admin_required

from .. import db

from ..models import (
    AdminUser,
    AdminSession,
    AuditLog,
    Customer,
    Order,
    Refund,
    SupportTicket
)

from ..extensions import bcrypt





def create_log(action, target=None):

    log = AuditLog(
        admin_id=session.get("admin_id"),
        action=action,
        target=target,
        ip_address=request.remote_addr
    )

    db.session.add(log)






# ==========================
# DASHBOARD
# ==========================

@admin.route("/")
@admin_required()
def dashboard():

    total_admins = AdminUser.query.count()

    total_customers = Customer.query.count()

    total_orders = Order.query.count()

    pending_orders = Order.query.filter_by(
        status="Pending"
    ).count()


    recent_logs = AuditLog.query.order_by(
        AuditLog.created_at.desc()
    ).limit(10).all()


    recent_orders = Order.query.order_by(
        Order.created_at.desc()
    ).limit(10).all()


    return render_template(
        "admin/dashboard.html",
        total_admins=total_admins,
        total_customers=total_customers,
        total_orders=total_orders,
        pending_orders=pending_orders,
        recent_logs=recent_logs,
        recent_orders=recent_orders
    )






# ==========================
# ADMIN MANAGEMENT
# ==========================

@admin.route("/admins")
@admin_required(role="Owner")
def admins():

    users = AdminUser.query.all()

    return render_template(
        "admin/admins.html",
        users=users
    )





@admin.route("/admins/create", methods=["GET","POST"])
@admin_required(role="Owner")
def create_admin():


    if request.method == "POST":

        username = request.form.get("username")

        email = request.form.get("email")

        password = request.form.get("password")

        role = request.form.get("role")



        existing = AdminUser.query.filter(
            (AdminUser.username == username) |
            (AdminUser.email == email)
        ).first()



        if existing:

            flash(
                "Username or email already exists",
                "danger"
            )

            return redirect(
                url_for("admin.create_admin")
            )



        new_admin = AdminUser(

            username=username,

            email=email,

            password_hash=bcrypt.generate_password_hash(
                password
            ).decode("utf-8"),

            role=role

        )


        db.session.add(new_admin)



        create_log(
            f"{session.get('username')} created admin",
            username
        )


        db.session.commit()



        flash(
            "Admin created",
            "success"
        )


        return redirect(
            url_for("admin.admins")
        )



    return render_template(
        "admin/create_admin.html"
    )






@admin.route("/admins/<int:id>/disable")
@admin_required(role="Owner")
def disable_admin(id):

    user = AdminUser.query.get_or_404(id)


    user.enabled = False


    create_log(
        f"{session.get('username')} disabled admin",
        user.username
    )


    db.session.commit()


    return redirect(
        url_for("admin.admins")
    )







@admin.route("/admins/<int:id>/enable")
@admin_required(role="Owner")
def enable_admin(id):

    user = AdminUser.query.get_or_404(id)


    user.enabled = True


    create_log(
        f"{session.get('username')} enabled admin",
        user.username
    )


    db.session.commit()


    return redirect(
        url_for("admin.admins")
    )







@admin.route("/admins/<int:id>/delete")
@admin_required(role="Owner")
def delete_admin(id):

    user = AdminUser.query.get_or_404(id)


    create_log(
        f"{session.get('username')} deleted admin",
        user.username
    )


    db.session.delete(user)

    db.session.commit()



    flash(
        "Admin deleted",
        "success"
    )


    return redirect(
        url_for("admin.admins")
    )







# ==========================
# CUSTOMERS
# ==========================

@admin.route("/customers")
@admin_required()
def customers():

    search = request.args.get("search")


    if search:

        customers = Customer.query.filter(
            (Customer.name.contains(search)) |
            (Customer.email.contains(search))
        ).all()

    else:

        customers = Customer.query.all()



    return render_template(
        "admin/customers.html",
        customers=customers
    )







@admin.route("/customers/<int:id>")
@admin_required()
def customer_detail(id):

    customer = Customer.query.get_or_404(id)


    orders = Order.query.filter_by(
        customer_id=id
    ).all()


    tickets = SupportTicket.query.filter_by(
        customer_id=id
    ).all()


    return render_template(
        "admin/customer_detail.html",
        customer=customer,
        orders=orders,
        tickets=tickets
    )







@admin.route("/customers/<int:id>/ban")
@admin_required()
def ban_customer(id):

    customer = Customer.query.get_or_404(id)


    customer.banned = True


    create_log(
        "Banned customer",
        customer.email
    )


    db.session.commit()


    return redirect(
        url_for(
            "admin.customer_detail",
            id=id
        )
    )







@admin.route("/customers/<int:id>/unban")
@admin_required()
def unban_customer(id):

    customer = Customer.query.get_or_404(id)


    customer.banned = False


    create_log(
        "Unbanned customer",
        customer.email
    )


    db.session.commit()


    return redirect(
        url_for(
            "admin.customer_detail",
            id=id
        )
    )








# ==========================
# ORDERS
# ==========================

@admin.route("/orders")
@admin_required()
def orders():

    orders = Order.query.order_by(
        Order.created_at.desc()
    ).all()


    return render_template(
        "admin/orders.html",
        orders=orders
    )







@admin.route("/orders/<int:id>/status/<status>")
@admin_required()
def update_order_status(id,status):

    order = Order.query.get_or_404(id)


    order.status = status


    create_log(
        "Updated order status",
        f"Order #{id}"
    )


    db.session.commit()


    return redirect(
        url_for("admin.orders")
    )







@admin.route("/orders/<int:id>/refund")
@admin_required()
def refund_order(id):

    order = Order.query.get_or_404(id)



    refund = Refund(

        order_id=order.id,

        amount=order.amount,

        reason="Admin refund"

    )


    order.status = "Refunded"


    create_log(
        "Refunded order",
        f"Order #{id}"
    )



    db.session.add(refund)

    db.session.commit()



    return redirect(
        url_for("admin.orders")
    )








# ==========================
# DEVICES
# ==========================

@admin.route("/devices")
@admin_required()
def devices():

    sessions = AdminSession.query.order_by(
        AdminSession.last_active.desc()
    ).all()


    return render_template(
        "admin/devices.html",
        sessions=sessions
    )







# ==========================
# AUDIT LOGS
# ==========================

@admin.route("/logs")
@admin_required()
def logs():

    logs = AuditLog.query.order_by(
        AuditLog.created_at.desc()
    ).all()


    return render_template(
        "admin/audit_logs.html",
        logs=logs
    )