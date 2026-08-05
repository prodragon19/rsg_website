from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth = Blueprint('auth', __name__)

# Enkel användare (senare kan du ha databas)
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

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('views.home'))

@auth.route('/signup')
def signup():
    return "<h3>Sign up page coming soon</h3>"