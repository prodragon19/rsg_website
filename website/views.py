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