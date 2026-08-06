from functools import wraps

from flask import session, redirect, url_for, flash



def admin_required(role=None):

    def decorator(function):

        @wraps(function)

        def wrapper(*args, **kwargs):

            if not session.get("logged_in"):

                return redirect(
                    url_for("auth.login")
                )


            if role:

                if session.get("role") != role:

                    flash(
                        "Permission denied",
                        "danger"
                    )

                    return redirect(
                        url_for("admin.dashboard")
                    )


            return function(
                *args,
                **kwargs
            )

        return wrapper

    return decorator