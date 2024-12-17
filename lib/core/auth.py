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
    
    @staticmethod
    def pop_session():
        session.pop('user_id', None)
        session.pop('session_token', None)
        session.pop('fullname', None)
        session.pop('user_role', None)
        session.pop('client_info', None)

    def get_user_info(self, email):
        try:
            query = "SELECT id, username, fullname, role FROM users WHERE email = %s;"
            with self.db.conn.cursor() as cursor:
                cursor.execute(query, (email,))
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "username": result[1],
                        "fullname": result[2],
                        'user_role': result[3]
                    }
                return None
        except Exception as e:
            print(f"Error fetching user info by email: {e}")
            return None

    @staticmethod
    def generate_random_key(length=32):
        """Generates a random key using ascii_letters, digits, and punctuation."""
        characters = string.ascii_letters + string.digits + string.punctuation
        random_key = ''.join(secrets.choice(characters) for _ in range(length))
        return random_key

    def authenticate(self, user_id, userinfo):
        client_info = session.get('client_info')
        if not client_info['http_agent'] or not client_info['http_user']:
            return {'status': 'error', 'message': 'HTTP_AGENT or HTTP_USER missing', 'status_code': 300}

        user_role = userinfo['userrole']
        user_name = userinfo['username']
        session_token = self.generate_random_key() 
        session['session_token'] = session_token
        session['user_id'] = user_id
        session['fullname'] = user_name
        session['user_role'] = user_role 
        session['client_info'] = {
            'http_agent': client_info['http_agent'],
            'http_user': client_info['http_user']
        }
        print(f"Session token set: {session['session_token']}")
        print(f'auth # agent : {client_info['http_agent']} | ip : {client_info['http_user']}')

        query = "INSERT INTO login_log (user_id, session_token, http_agent, http_user) VALUES (%s, %s, %s, %s)"
        self.db.cursor.execute(query, (user_id, session_token, client_info['http_agent'], client_info['http_user']))
        self.db.conn.commit()
        print(f"Log updated: User id: {user_id} | session token: {session_token} | http_agent: {client_info['http_agent']} | http_user: {client_info['http_user']}")

        return {'status': 'success', 'message': 'User authenticated and session token generated', 'status_code': 200}
    
    @staticmethod
    def is_authorized():
        session_token = session.get('session_token')
        user_id = session.get('user_id')
        client_info = session.get('client_info')
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
                auth.pop_session()
                return False 
                
            
            user_id_log, session_token_db, http_agent, http_user, login_time = result
            
            if user_id != user_id_log:
                print('user id mismatch')
                auth.pop_session()
                return False  
            
            if not client_info.get('http_agent') or not client_info.get('http_user'):
                print('client http missing')
                auth.pop_session()
                return False
            
            if (datetime.now() - login_time).total_seconds() > 3600: 
                print(f'login time expired, Logged in before : {(datetime.now() - login_time).total_seconds()}')
                auth.pop_session()
                return False
            
            if http_agent == client_info['http_agent'] and http_user == client_info['http_user']:
                return True  
            
            print('client and server http mismatch')
            auth.pop_session()
            return False 

        except Exception as e:
            print(f"Error during authorization: {e}")
            auth.pop_session()
            return False  
