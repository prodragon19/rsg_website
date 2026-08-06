# website/views.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from . import db  # Import SQLAlchemy instance from __init__.py
from .models import NewsletterPost  # Import our newsletter model

views = Blueprint('views', __name__)

# ������������������ IMAGE UPLOAD CONFIGURATION (KEEP THESE CONSTANTS)
UPLOAD_FOLDER = 'static/uploads'  # ← RELATIVE PATH (we'll resolve it with current_app)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ========== PUBLIC ROUTES (UNCHANGED) ==========
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

# ========== NEWSLETTER ROUTES (FULLY IMPLEMENTED) ==========
@views.route('/newsletter')
def newsletter():
    posts = NewsletterPost.query.order_by(NewsletterPost.date_posted.desc()).all()
    return render_template('newsletter.html', posts=posts)

@views.route('/newsletter/<int:post_id>')
def newsletter_detail(post_id):
    post = NewsletterPost.query.get_or_404(post_id)
    return render_template('newsletter_detail.html', post=post)

@views.route('/admin/newsletter', methods=['GET', 'POST'])
def admin_newsletter():
    if not session.get('logged_in') or session.get('username') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        author = request.form.get('author', '').strip() or 'Anonymous'
        
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Validation
                if file.content_length > MAX_FILE_SIZE:
                    flash('Image too large! Max 5MB allowed.', 'error')
                    return redirect(url_for('views.admin_newsletter'))
                
                if not allowed_file(file.filename):
                    flash('Invalid image type! Use JPG, PNG, or GIF.', 'error')
                    return redirect(url_for('views.admin_newsletter'))
                
                # Save file securely
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"{timestamp}_{filename}"
                
                # Get absolute upload path from app config
                upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
                os.makedirs(upload_path, exist_ok=True)  # Ensure dir exists
                file.save(os.path.join(upload_path, image_filename))

        # Validate required fields
        if not title:
            flash('Title is required!', 'error')
            return redirect(url_for('views.admin_newsletter'))
        if not content:
            flash('Content is required!', 'error')
            return redirect(url_for('views.admin_newsletter'))

        # Save to database
        new_post = NewsletterPost(
            title=title,
            content=content,
            author=author,
            image_filename=image_filename
        )
        db.session.add(new_post)
        db.session.commit()
        
        flash('Newsletter posted successfully!', 'success')
        return redirect(url_for('views.newsletter'))

    return render_template('admin_newsletter.html')

@views.route('/newsletter/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_newsletter(post_id):
    if not session.get('logged_in') or session.get('username') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('views.home'))
    
    post = NewsletterPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.title = request.form.get('title', '').strip()
        post.content = request.form.get('content', '').strip()
        post.author = request.form.get('author', '').strip() or 'Anonymous'
        
        # Handle image upload (replacement)
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Validation
                if file.content_length > MAX_FILE_SIZE:
                    flash('Image too large! Max 5MB allowed.', 'error')
                    return redirect(url_for('views.edit_newsletter', post_id=post.id))
                
                if not allowed_file(file.filename):
                    flash('Invalid image type! Use JPG, PNG, or GIF.', 'error')
                    return redirect(url_for('views.edit_newsletter', post_id=post.id))
                
                # Delete old image if exists
                if post.image_filename:
                    old_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, post.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Save new image
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                post.image_filename = f"{timestamp}_{filename}"
                
                upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
                os.makedirs(upload_path, exist_ok=True)  # Ensure dir exists
                file.save(os.path.join(upload_path, post.image_filename))
        
        # Validate
        if not post.title or not post.content:
            flash('Title and content are required!', 'error')
            return redirect(url_for('views.edit_newsletter', post_id=post.id))
        
        db.session.commit()
        flash('Newsletter updated!', 'success')
        return redirect(url_for('views.newsletter_detail', post_id=post.id))
    
    return render_template('edit_newsletter.html', post=post)

@views.route('/newsletter/<int:post_id>/delete', methods=['POST'])
def delete_newsletter(post_id):
    if not session.get('logged_in') or session.get('username') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('views.home'))
    
    post = NewsletterPost.query.get_or_404(post_id)
    
    # Delete associated image file
    if post.image_filename:
        image_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, post.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Delete from database
    db.session.delete(post)
    db.session.commit()
    flash('Newsletter deleted!', 'success')
    return redirect(url_for('views.newsletter'))
