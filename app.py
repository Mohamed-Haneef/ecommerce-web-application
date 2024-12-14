from flask import Flask, render_template, redirect, request, session, url_for, jsonify
from requests_oauthlib import OAuth2Session
from flask_bcrypt import bcrypt
from lib import database as _database
from lib import signup as _signup
from lib import login as _login
from lib import oauth as _oauth
from lib import user as _user
from lib import auth as _auth
import os
# from lib import login, signup, product, user, database, searchbar

app = Flask(__name__)
app.secret_key = os.urandom(24)  

DOMAIN = os.getenv('DOMAIN')


@app.route('/')
def home():

    return render_template('index.html')



@app.route('/login')
def login():
	return render_template('login.html', DOMAIN=DOMAIN, GOOGLE_OAUTH_PATH=GOOGLE_OAUTH_PATH)



@app.route('/signup')
def signup():
	return render_template('signup.html')



@app.route('/oauth/google')
def oauth_google():
    
    client_info = {
            'http_agent': request.headers.get('User-Agent'),
            'http_user': request.remote_addr
        }

    session['client_info'] = client_info
    oauth_instance = _oauth()
    oauth2 = oauth_instance.create_oauth_session()
    authorization_url, state = oauth2.authorization_url(oauth_instance.AUTHORIZATION_BASE_URL)

    session['oauth_state'] = state
    print(f"Auth URL: {authorization_url} | State: {state}")

    return redirect(authorization_url)


@app.route('/profile')
def profile():
	return render_template('profile.html')

@app.route('/oauth/callback')
def callback():
    try:
        state = session.get('oauth_state')
        client_info = session.get('client_info')

        if not state:
            return "State is missing. Retry logging in.", 400
        if not client_info:
            return "Client details missing. Retry logging in.", 400

        oauth_instance = _oauth()
        oauth2 = oauth_instance.create_oauth_session(state)

        token_response = oauth2.fetch_token(
            oauth_instance.TOKEN_URL, 
            authorization_response=request.url,
            client_secret=oauth_instance.GOOGLE_CLIENT_SECRET
        )

        if not token_response or 'access_token' not in token_response:
            return "Failed to retrieve the access token.", 400

        user_info = oauth_instance.get_user_info(oauth2.token)
        if not user_info or 'email' not in user_info:
            return "Failed to retrieve user information.", 400

        oauth_response = oauth_instance.oauth_login(user_info, client_info)

        print("OAuth response:", oauth_response)

        if oauth_response['status'] == 'error':
            return jsonify(oauth_response), oauth_response.get('status_code', 400)

        return render_template('profile.html', oauth=oauth_response)
    except Exception as e:
        print(f"Callback error: {e}")
        return "An error occurred during the OAuth process. Please try again later.", 500


@app.route('/logout')
def logout():
    session.pop('oauth_state', None)
    session.pop('user_info', None)
    
    return redirect(url_for('profile'))


@app.route('/api/v1/user/signup', methods=['POST'])
def api_signup():
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

@app.route('/api/v1/user/login', methods=['POST'])
def api_login():
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8444, ssl_context=('cert.crt', 'cert.key'))
