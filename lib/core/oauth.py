from requests_oauthlib import OAuth2Session
import os
from lib.utils.database import database
from flask import session
from lib.core.auth import auth 
import string
import random

class oauth:
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')

    AUTHORIZATION_BASE_URL = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URL = 'https://oauth2.googleapis.com/token'
    API_BASE_URL = 'https://www.googleapis.com/'

    CLIENT_SCOPE = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email"
    ]

    def __init__(self):
        self.db = database()

    def create_oauth_session(self, state=None, token=None):
        return OAuth2Session(
            self.GOOGLE_CLIENT_ID,
            redirect_uri=self.GOOGLE_REDIRECT_URI,
            scope=self.CLIENT_SCOPE,
            state=state,
            token=token
        )
    def check_duplicate_entry(self, table, **kwargs):
        if not table:
            raise ValueError("Table name cannot be empty.")
        
        try:
            query = f"SELECT * FROM {table} WHERE "
            conditions = [f"{key} = %s" for key in kwargs]
            query += " AND ".join(conditions)

            self.db.cursor.execute(query, tuple(kwargs.values()))
            result = self.db.cursor.fetchone()

            if result:
                return True 
                
            return None
        except Exception as e:
            print(f"Error checking for duplicate entries: {e}")
            return None


    @staticmethod
    def generate_random_key(length=32):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def get_user_info(self, token):
        oauth_session = self.create_oauth_session(token=token)
        response = oauth_session.get(f"{self.API_BASE_URL}oauth2/v3/userinfo")
        return response.json()
    


    def oauth_signup(self, user_info, client_info):
        try:
            duplicate_entry = self.check_duplicate_entry('users', email=user_info['email'])
            if duplicate_entry:
                return {'status': 'error', 'message': 'User already exists', 'status_code': 409}

            rand_suffix = str(random.randint(100, 9999))
            gen_username = user_info['username'].strip().lower().replace(" ", "") + rand_suffix

            insert_user_query = """
                INSERT INTO users (email, username, fullname, dob)
                VALUES (%s, %s, %s, %s) RETURNING id, role
            """
            self.db.cursor.execute(
                insert_user_query,
                (user_info['email'], gen_username, user_info['username'], user_info.get('dob', None))
            )
            result = self.db.cursor.fetchone()
            if result is None:
                return {'status': 'error', 'message': 'Failed to retrieve user ID', 'status_code': 500}

            user_id = result[0]
            user_role = result[1]

            insert_auth_query = """
                INSERT INTO auth (user_id, oauth_provider, oauth_id)
                VALUES (%s, %s, %s)
            """
            self.db.cursor.execute(insert_auth_query, (user_id, user_info['oauth_provider'], user_info['oauth_id']))
            self.db.conn.commit()

            auth_instance = auth()  
            usr = {
                'username': user_info['username'],
                'userrole': user_role
            }
            auth_instance.authenticate(user_id, userinfo=usr) 

            return {'status': 'success', 'message': 'User created and logged in via OAuth', 'user_id': user_id, 'status_code': 200}
        
        except Exception as e:
            self.db.conn.rollback()
            print(f"Error during OAuth signup: {e}")
            return {'status': 'error', 'message': f'Error during OAuth signup: {e}', 'status_code': 500}

    def oauth_login(self, user_info, client_info):
        try:
            existing_user = self.check_duplicate_entry('users', email=user_info['email'])
            
            if existing_user:
                existing_auth = self.check_duplicate_entry('auth', oauth_provider='google', oauth_id=user_info['sub'])
                print(f' \n \n oauth_id: {user_info['sub']} \n \n')
                if existing_auth:
                    print(f'Existing auth: {existing_auth}')
                    auth_instance = auth() 
                    u_info = auth_instance.get_user_info(user_info['email'])
                    usr = {
                        'username': u_info['fullname'],
                        'userrole': u_info['user_role']
                    }
                    auth_instance.authenticate(u_info['id'], userinfo=usr)  

                    return {'status': 'success', 'message': 'User logged in via OAuth', 'status_code': 200}
                
                self.link_oauth_account(existing_user['id'], user_info)
                return {'status': 'success', 'message': 'OAuth credentials linked to existing user', 'status_code': 200}

            new_user = {
                "email": user_info['email'],
                "username": user_info.get('name', 'Unknown User'),
                "dob": user_info.get('dob', None),
                "oauth_provider": "google",
                "oauth_id": user_info['sub'],
                "profile_picture": user_info.get('picture', None)
            }
            user_creation_response = self.oauth_signup(new_user, client_info)
            if user_creation_response['status'] == 'error':
                return user_creation_response

            return {'status': 'success', 'message': 'New user created and logged in via OAuth', 'status_code': 200}
        
        except Exception as e:
            print(f"Error during OAuth login: {e}")
            return {'status': 'error', 'message': f'Unexpected error: {e}', 'status_code': 500}


    def link_oauth_account(self, user_id, user_info):
        try:
            existing_auth = self.check_duplicate_entry('auth', user_id=user_id, oauth_provider='google')
            if existing_auth:
                return {'status': 'error', 'message': 'OAuth credentials already linked', 'status_code': 409}
            
            insert_auth_query = """
                INSERT INTO auth (user_id, oauth_provider, oauth_id)
                VALUES (%s, %s, %s)
            """
            self.db.cursor.execute(insert_auth_query, (user_id, 'google', user_info['sub']))
            self.db.conn.commit()
        except Exception as e:
            self.db.conn.rollback()
            print(f"Error linking OAuth account: {e}")
            return {'status': 'error', 'message': f'Error linking OAuth account: {e}', 'status_code': 500}
