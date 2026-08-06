# models.py
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # For future auth

class NewsletterPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), default='Anonymous')
    image_filename = db.Column(db.String(200))  # Stores just the filename (e.g., "abc123.jpg")
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<NewsletterPost {self.title}>'
