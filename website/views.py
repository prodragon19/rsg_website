from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime

# �� SINGLE Blueprint definition (only one!)
views = Blueprint('views', __name__)

# ========== TEMPORARY STORAGE (for demo - use DB in production) ==========
POSTS = []

# ========== PUBLIC ROUTES ==========
@views.route('/')
@views.route('/Base')  # Remove the trailing space route ('/Base ') - it's unnecessary
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

# ========== NEWSLETTER ROUTES ==========
@views.route('/newsletter')
def newsletter():
    return render_template('newsletter.html', posts=POSTS)

@views.route('/admin/newsletter', methods=['GET', 'POST'])
def admin_newsletter():
    # ��� Admin protection (requires SECRET_KEY to be set in app factory)
    if not session.get('logged_in') or session.get('username') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('views.home'))  # Redirect to home instead of login (adjust as needed)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        # �� CRITICAL VALIDATION (prevents empty posts)
        if not title:
            flash('Title is required!', 'error')
            return redirect(url_for('views.admin_newsletter'))
        if not content:
            flash('Content is required!', 'error')
            return redirect(url_for('views.admin_newsletter'))

        # Add post with validation
        POSTS.insert(0, {
            "title": title,
            "content": content,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        flash('Newsletter posted successfully!', 'success')
        return redirect(url_for('views.newsletter'))

    return render_template('admin_newsletter.html')
