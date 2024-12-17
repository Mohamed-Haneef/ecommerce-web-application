from flask import Blueprint, render_template, request, redirect, url_for, session
from lib import auth as _auth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    client_info = {
            'http_agent': request.headers.get('User-Agent'),
            'http_user': request.remote_addr
    }
    session['client_info'] = client_info
    if _auth.is_authorized():
        return redirect(url_for('home_bp.home_page'))
    else:
        return render_template('login.html')

@auth_bp.route('/signup')
def signup():
    client_info = {
            'http_agent': request.headers.get('User-Agent'),
            'http_user': request.remote_addr
        }

    session['client_info'] = client_info
    if _auth.is_authorized():
        return redirect(url_for('home_bp.home_page'))
    else:
        return render_template('signup.html')

@auth_bp.route('/logout')
def logout():
    _auth.pop_session()
    return redirect(url_for('auth.login'))