from flask import Blueprint, render_template, session

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
def profile():
    return render_template('profile.html')