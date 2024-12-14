import bcrypt
import secrets
import string
from flask import session
from datetime import datetime, timedelta
from lib.utils.database import database
import hashlib

class auth:
    def __init__(self):
        self.db = database()
        self.session_token = session.get('session_token')
        self.user_id = session.get('user_id')
    
    def get_user_id(self, email):
        try:
            query = "SELECT id FROM users WHERE email = %s;"
            with self.db.conn.cursor() as cursor: 
                cursor.execute(query, (email,))
                result = cursor.fetchone()  
                return result[0] if result else None 
        except Exception as e:
            print(f"Error fetching user ID by email: {e}")
            return None


    @staticmethod
    def generate_random_key(length=32):
        """Generates a random key using ascii_letters, digits, and punctuation."""
        characters = string.ascii_letters + string.digits + string.punctuation
        random_key = ''.join(secrets.choice(characters) for _ in range(length))
        return random_key

    def authenticate(self, user_id, client_info):
        """Authenticate the user and generate a session token."""
        if not client_info['http_agent'] or not client_info['http_user']:
            return {'status': 'error', 'message': 'HTTP_AGENT or HTTP_USER missing', 'status_code': 300}

        session_token = self.generate_random_key() 
        session['session_token'] = session_token
        session['user_id'] = user_id
        print(f'auth # agent : {client_info['http_agent']} | ip : {client_info['http_user']}')

        query = "INSERT INTO login_log (user_id, session_token, http_agent, http_user) VALUES (%s, %s, %s, %s)"
        self.db.cursor.execute(query, (user_id, session_token, client_info['http_agent'], client_info['http_user']))
        self.db.conn.commit()
        print(f"Log updated: User id: {user_id} | session token: {session_token} | http_agent: {client_info['http_agent']} | http_user: {client_info['http_user']}")

        return {'status': 'success', 'message': 'User authenticated and session token generated', 'status_code': 200}

    def authorize(self, client_info):
        if not self.session_token:
            return {'status': 'error', 'message': 'Session token missing', 'status_code': 400}

        query = "SELECT user_id, session_token, http_agent, http_user, login_time FROM login_log WHERE session_token = %s"
        self.db.cursor.execute(query, (self.session_token,))
        result = self.db.cursor.fetchone()

        if not result:
            return {'status': 'error', 'message': 'Session token not found', 'status_code': 400}

        self.user_id_log, self.session_token_db, self.http_agent, self.http_user, self.login_time = result

        if not client_info.http_agent or not client_info.http_user:
            return {'status': 'error', 'message': 'HTTP_AGENT or HTTP_USER missing', 'status_code': 400}

        if self.user_id == self.user_id_log and self.http_agent == client_info.http_agent and self.http_user == client_info.http_user:
            return {'status': 'error', 'message': 'Session already authenticated', 'status_code': 409}

        if (datetime.now() - self.login_time).total_seconds() > 3600:  
            time_remaining = (datetime.now() - self.login_time).total_seconds()
            print(f'Time remaining for the login session: {time_remaining}')
            return {'status': 'error', 'message': 'Session expired', 'status_code': 401}

        return {'status': 'success', 'message': 'User authorized', 'status_code': 200}
