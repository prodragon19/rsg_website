from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import os
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)

# ���������� IMAGE UPLOAD CONFIGURATION
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ���������� TEMPORARY STORAGE (Replace with database in production)
POSTS = []

# ========== PUBLIC ROUTES ==========
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

# ========== NEWSLETTER ROUTES ==========
@views.route('/newsletter')
def newsletter():
    return render_template('newsletter.html', posts=POSTS)

@views.route('/admin/newsletter', methods=['GET', 'POST'])
def admin_newsletter():
    # Admin protection
    if not session.get('logged_in') or session.get('username') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        # ���������� GET ALL FORM DATA
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        author = request.form.get('author', '').strip() or 'Anonymous'
        
        # ���������� HANDLE IMAGE UPLOAD
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':  # User selected a file
                # ���������� VALIDATIONS
                if file.content_length > MAX_FILE_SIZE:
                    flash('Image too large! Max 5MB allowed.', 'error')
                    return redirect(url_for('views.admin_newsletter'))
                
                if not allowed_file(file.filename):
                    flash('Invalid image type! Use JPG, PNG, or GIF.', 'error')
                    return redirect(url_for('views.admin_newsletter'))
                
                # ���������� SAVE FILE SECURELY
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"{timestamp}_{filename}"
                
                # Create uploads directory if missing
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, image_filename))

        # ���������� VALIDATE REQUIRED FIELDS
        if not title:
            flash('Title is required!', 'error')
            return redirect(url_for('views.admin_newsletter'))
        if not content:
            flash('Content is required!', 'error')
            return redirect(url_for('views.admin_newsletter'))

        # ���������� CREATE POST WITH ALL FIELDS
        POSTS.insert(0, {
            "title": title,
            "content": content,
            "author": author,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "image": image_filename  # None if no image uploaded
        })
        flash('Newsletter posted successfully!', 'success')
        return redirect(url_for('views.newsletter'))

    return render_template('admin_newsletter.html')
