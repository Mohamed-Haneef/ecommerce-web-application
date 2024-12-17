import bcrypt
from flask import session
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
        print('vc called')
        if not self.valid:
            return {'status': 'error', 'message': 'Identifier and password are required', 'status_code': 400}
        print('i am valid')
        try:
            query = """
            SELECT u.id, u.username, u.fullname, u.email, u.role, u.mobile, a.password_hash
            FROM users u
            JOIN auth a ON u.id = a.user_id
            WHERE u.email = %s
            """
            self.db.cursor.execute(query, (self.identifier,))
            print('executed')
            result = self.db.cursor.fetchone()

            print(f'\n\n result: {result} \n \n')

            if not result:
                return {'status': 'error', 'message': 'Invalid email or password', 'status_code': 404}

            self.user_id, self.username, self.fullname, self.email, self.user_role, self.mobile, self.password_hash = result
            user_cred = {
                'user_id': self.user_id,
                'email': self.email,
                'username': self.username,
                'fullname': self.fullname,
                'userrole': self.user_role
            }

            return {'status': 'success', 'message': 'Credentials validated', 'status_code': 200, 'user_cred': user_cred}
        except Exception as e:
            return {'status': 'error', 'message': f'Internal error: {self.password_hash}', 'status_code': 500}


    def login_user(self):
        print("i am called")
        credentials_validation = self.validate_credentials()
        print(f'\n\n credential validation: {credentials_validation} \n \n')
        if credentials_validation['status'] != 'success':
            return credentials_validation
        try:
            print(self.user_id, self.username, self.email, self.mobile, self.password_hash)
            print(self.password.encode('utf-8'), self.password_hash.encode('utf-8'))
            if bcrypt.checkpw(self.password.encode('utf-8'), self.password_hash.encode('utf-8')):
                # print(f'auth # agent : {client_info['http_agent']} | ip : {client_info['http_user']}')
                authentication = auth()
                usr = {
                    'username': self.fullname,
                    'userrole': self.user_role
                }
                auth_status = authentication.authenticate(user_id=self.user_id,userinfo=usr)
                print(auth_status)
                return {'status': 'success', 'message': 'Login successful', 'status_code': 200}
            else:
                return {'status': 'error', 'message': 'Invalid email or password', 'status_code': 401}
        except Exception as bcrypt_error:
            print(f"Bcrypt error: {bcrypt_error}")
            return {'status': 'error', 'message': 'Internal server error', 'status_code': 500}