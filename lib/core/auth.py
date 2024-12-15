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
        print(f"Session token set: {session['session_token']}")
        print(f'auth # agent : {client_info['http_agent']} | ip : {client_info['http_user']}')

        query = "INSERT INTO login_log (user_id, session_token, http_agent, http_user) VALUES (%s, %s, %s, %s)"
        self.db.cursor.execute(query, (user_id, session_token, client_info['http_agent'], client_info['http_user']))
        self.db.conn.commit()
        print(f"Log updated: User id: {user_id} | session token: {session_token} | http_agent: {client_info['http_agent']} | http_user: {client_info['http_user']}")

        return {'status': 'success', 'message': 'User authenticated and session token generated', 'status_code': 200}
    
    @staticmethod
    def is_authorized(client_info):
        session_token = session.get('session_token')
        user_id = session.get('user_id')
        db = database()
        
        print(f'session_token at auth stage{session_token}')
        print(f'user-id at auth stage{user_id}')
        if not session_token or not user_id:
            print('session id or uid not found')
            return False  
        
        try:
            query = "SELECT user_id, session_token, http_agent, http_user, login_time FROM login_log WHERE session_token = %s"
            db.cursor.execute(query, (session_token,))
            result = db.cursor.fetchone()
            
            if not result:
                print('session token not found in the database')
                return False 
                
            
            user_id_log, session_token_db, http_agent, http_user, login_time = result
            
            if user_id != user_id_log:
                print('user id mismatch')
                return False  
            
            if not client_info.get('http_agent') or not client_info.get('http_user'):
                print('client http missing')
                return False
            
            if (datetime.now() - login_time).total_seconds() > 3600: 
                print(f'login time expired, Logged in before : {(datetime.now() - login_time).total_seconds()}')
                return False
            
            if http_agent == client_info['http_agent'] and http_user == client_info['http_user']:
                return True  
            
            print('client and server http mismatch')
            return False 

        except Exception as e:
            print(f"Error during authorization: {e}")
            return False  
