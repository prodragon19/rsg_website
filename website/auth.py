from flask import Blueprint, render_template, request, redirect, url_for, session

auth = Blueprint('auth', __name__)

# Temporary user storage (resets when the server restarts)
USERS = {
    "admin": "1234"
}

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('views.home'))
        else:
            return render_template('login.html', error="Wrong username or password")

    return render_template('login.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if not username or not password:
            return render_template('signup.html', error="Please fill in all fields")

        if password != confirm:
            return render_template('signup.html', error="Passwords do not match")

        if username in USERS:
            return render_template('signup.html', error="Username already exists")

        # Add the new user
        USERS[username] = password

        return render_template('signup.html', success="Account created! You can now log in.")

    return render_template('signup.html')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('views.home'))