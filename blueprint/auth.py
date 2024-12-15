from flask import Blueprint, render_template, request, redirect, url_for, session

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    client_info = {
            'http_agent': request.headers.get('User-Agent'),
            'http_user': request.remote_addr
        }

    session['client_info'] = client_info
    return render_template('login.html')

@auth_bp.route('/signup')
def signup():
    client_info = {
            'http_agent': request.headers.get('User-Agent'),
            'http_user': request.remote_addr
        }

    session['client_info'] = client_info
    return render_template('signup.html')

@auth_bp.route('/logout')
def logout():
    client_info = {
            'http_agent': request.headers.get('User-Agent'),
            'http_user': request.remote_addr
        }

    session['client_info'] = client_info
    session.pop('user_info', None)
    return redirect(url_for('auth.login'))