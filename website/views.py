from flask import Blueprint, render_template

views = Blueprint('views', __name__)

# Startsida (stödjer både / och /Base pga felaktiga länkar i templates)
@views.route('/')
@views.route('/Base')
@views.route('/Base ')
def home():
    return render_template('base.html')

@views.route('/about')
def about():
    return render_template('about.html')

@views.route('/aircraft')
def aircraft():
    return render_template('aircraft.html')

@views.route('/contact')
@views.route('/Contact')
def contact():
    return render_template('contact.html')

@views.route('/work-at-rsg')
def work_at_rsg():
    return render_template('work-at-rsg.html')
    from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import datetime

views = Blueprint('views', __name__)

# Temporary storage (disappears when server restarts)
POSTS = []

@views.route('/')
@views.route('/Base')
def home():
    return render_template('base.html')

@views.route('/about')
def about():
    return render_template('about.html')

@views.route('/aircraft')
def aircraft():
    return render_template('aircraft.html')

@views.route('/contact')
@views.route('/Contact')
def contact():
    return render_template('contact.html')

@views.route('/work-at-rsg')
def work_at_rsg():
    return render_template('work-at-rsg.html')

# ========== NEWSLETTER ==========

@views.route('/newsletter')
def newsletter():
    return render_template('newsletter.html', posts=POSTS)

@views.route('/admin/newsletter', methods=['GET', 'POST'])
def admin_newsletter():
    # Only allow admin
    if not session.get('logged_in') or session.get('username') != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        POSTS.insert(0, {
            "title": title,
            "content": content,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        return redirect(url_for('views.newsletter'))

    return render_template('admin_newsletter.html')