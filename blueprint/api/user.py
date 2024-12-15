from flask import Blueprint, jsonify, request, session
from lib import login as _login
from lib import signup as _signup

user_bp = Blueprint('user_api', __name__, url_prefix='/api/v1/user')

@user_bp.route('/signup', methods=['POST'])
def api_signup():
    client_info = {
            'http_agent': request.headers.get('User-Agent'),
            'http_user': request.remote_addr
        }

    session['client_info'] = client_info
    try:
        if request.is_json:
            userdata = request.json
        elif request.form:
            userdata = request.form.to_dict()
        else:
            return jsonify({'error': 'No data provided'}), 400
        
        userdict = {
            "email": userdata.get('email'),
            "username": userdata.get('username'),
            "dob": userdata.get('dob'),
            "mobile": userdata.get('mobile'),
            "password": userdata.get('password')
        }
        
        if not all(userdict.values()):
            return jsonify({'error': 'Mandatory field elements missing'}), 400
        
        user_creation = _signup(userdict)
        creation_status = user_creation.signup_user()

        return jsonify({
            f'{creation_status["status"]}': f'{creation_status["message"]}'
        }), int(creation_status["status_code"])
    except Exception as e:
        print(f"Got Exception: {e}")
        
        try:
            if hasattr(user_creation, 'db') and hasattr(user_creation.db, 'conn'):
                user_creation.db.conn.rollback()  
        except Exception as rollback_error:
            print(f"Rollback failed: {rollback_error}")
        
        return jsonify({'error': f'Internal server error: {e}'}), 500

@user_bp.route('/login', methods=['POST'])
def api_login():
    client_info = {
            'http_agent': request.headers.get('User-Agent'),
            'http_user': request.remote_addr
        }

    session['client_info'] = client_info
    try:
        if request.is_json:
            userdata = request.json
        elif request.form:
            userdata = request.form.to_dict()
        else:
            return jsonify({'error': 'No data provided'}), 400
        
        userdict = {
            "identifier": userdata.get('identifier'),
            "password": userdata.get('password')
        }
        
        if not all(userdict.values()):
            return jsonify({'error': 'Mandatory field elements missing'}), 400
        
        user_login = _login(userdict)
        client_info = {
            'http_agent': request.headers.get('User-Agent'),
            'http_user': request.remote_addr 
        }
        login_status = user_login.login_user(client_info=client_info)
        if(login_status['status'] != 'success'):
            return jsonify({
            f'{login_status["status"]}': f'{login_status["message"]}'
        }), int(login_status["status_code"])
        print('login success')
        print(f'session_token: {session['session_token']} | user_id: {session['user_id']}')

        return jsonify({
            f'{login_status["status"]}': f'{login_status["message"]}'
        }), int(login_status["status_code"])
    except Exception as e:
        print(f"Got Exception: {e}")
        
        try:
            if hasattr(user_login, 'db') and hasattr(user_login.db, 'conn'):
                user_login.db.conn.rollback()  
        except Exception as rollback_error:
            print(f"Rollback failed: {rollback_error}")
        
        return jsonify({'error': f'Internal server error: {e}'}), 500

