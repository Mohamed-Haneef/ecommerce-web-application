import bcrypt
from lib.utils.database import database
from lib.core.auth import auth

class login:
    def __init__(self, userdata):
        self.identifier = userdata.get('identifier')
        self.password = userdata.get('password')
        self.db = database()
        
        if not self.identifier or not self.password:
            self.valid = False
        else:
            self.valid = True

    def validate_credentials(self):
        if not self.valid:
            return {'status': 'error', 'message': 'Identifier and password are required', 'status_code': 400}

        try:
            query = """
            SELECT u.id, u.username, u.email, u.mobile, a.password_hash
            FROM users u
            JOIN auth a ON u.id = a.user_id
            WHERE u.email = %s OR u.mobile = %s
            """
            self.db.cursor.execute(query, (self.identifier, self.identifier))
            result = self.db.cursor.fetchone()

            if not result:
                return {'status': 'error', 'message': 'User not found', 'status_code': 404}

            self.user_id, self.username, self.email, self.mobile, self.password_hash = result
            user_cred = {
                'user_id': self.user_id,
                'email': self.email,
                'username': self.username
            }

            return {'status': 'success', 'message': 'Credentials validated', 'status_code': 200, 'user_cred': user_cred}
        except Exception as e:
            return {'status': 'error', 'message': f'Internal error: {self.password_hash}', 'status_code': 500}


    def login_user(self, client_info):
        credentials_validation = self.validate_credentials()
        if credentials_validation['status'] != 'success':
            return credentials_validation

        try:
            print(self.user_id, self.username, self.email, self.mobile, self.password_hash)
            if bcrypt.checkpw(self.password.encode('utf-8'), self.password_hash.encode('utf-8')):
                print(f'auth # agent : {client_info['http_agent']} | ip : {client_info['http_user']}')
                authentication = auth()
                auth_status = authentication.authenticate(user_id=self.user_id, client_info=client_info)
                print(auth_status)
                return {'status': 'success', 'message': 'Login successful', 'status_code': 200}
            else:
                return {'status': 'error', 'message': 'Invalid password', 'status_code': 401}
        except Exception as bcrypt_error:
            print(f"Bcrypt error: {bcrypt_error}")
            return {'status': 'error', 'message': 'Internal server error', 'status_code': 500}