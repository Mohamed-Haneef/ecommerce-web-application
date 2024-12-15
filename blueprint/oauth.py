from flask import Blueprint, request, redirect, session, url_for, jsonify, render_template
from requests_oauthlib import OAuth2Session
from lib import oauth as _oauth 

oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')

@oauth_bp.route('/google')
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


@oauth_bp.route('/callback')
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
            return jsonify({oauth_response['status']: oauth_response['message']}), oauth_response['status_code']

        t_response =  jsonify({oauth_response['status']: oauth_response['message']}), oauth_response['status_code']
        return render_template('profile.html', oauth=t_response)
    except Exception as e:
        print(f"Callback error: {e}")
        return "An error occurred during the OAuth process. Please try again later.", 500
