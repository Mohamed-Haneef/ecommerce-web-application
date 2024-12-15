from flask import Blueprint, render_template, session, request
from lib import auth as _auth

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
def profile():
    client_info = {
            'http_agent': request.headers.get('User-Agent'),
            'http_user': request.remote_addr
        }
    auth_status = _auth.is_authorized(client_info)
    print(f'auth_status: {auth_status}')
    return render_template('profile.html', status=auth_status)
    
    