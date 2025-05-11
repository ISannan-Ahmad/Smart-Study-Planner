from flask import Blueprint, render_template
from flask_login import login_required


main = Blueprint("main", __name__)

from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')  # You'll create this later