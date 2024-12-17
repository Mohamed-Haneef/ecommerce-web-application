import bcrypt
from lib.utils.database import database
from flask import session
import random  
from lib.core.auth import auth as _auth

class signup:
    def __init__(self, userdata):
        self.username = userdata.get('username')
        self.email = userdata.get('email')
        self.mobile = userdata.get('mobile')
        self.dob = userdata.get('dob')
        self.password = userdata.get('password')
        self.db = database()

    def validate_inputs(self):
        if not all([self.username, self.email, self.mobile, self.dob, self.password]):
            return False
        return True

    def hash_password(self):
        try:
            salt = bcrypt.gensalt(rounds=15)
            hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), salt)
            return hashed_password.decode('utf-8')
        except Exception as e:
            print(f"Error hashing password: {e}")
            return None

    def check_duplicate_entry(self, table, **kwargs):
        if not table:
            raise ValueError("Table name cannot be empty.")

        try:
            query = f"SELECT * FROM {table} WHERE "
            conditions = [f"{key} = %s" for key in kwargs]
            query += " AND ".join(conditions)

            self.db.cursor.execute(query, tuple(kwargs.values()))
            result = self.db.cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Error checking for duplicate entries: {e}")
            return None

    def create_user(self):
        try:
            client_info=session.get('client_info')
            hashed_password = self.hash_password()
            if not hashed_password:
                return {'status': 'error', 'message': 'Password hashing failed', 'status_code': 500}

            rand_suffix = str(random.randint(100, 9999))
            gen_username = self.username.strip().lower().replace(" ", "") + rand_suffix

            insert_user_query = """
                INSERT INTO users (username, fullname, email, dob, mobile)
                VALUES (%s, %s, %s, %s, %s) RETURNING id, role
            """
            self.db.cursor.execute(
                insert_user_query, 
                (gen_username, self.username, self.email, self.dob, self.mobile)
            )
            return_data = self.db.cursor.fetchone()
            user_id = return_data[0]
            user_role = return_data[1]
            print(f'\n \n user_id returing : {user_id} \n \n \n')

            insert_auth_query = """
                INSERT INTO auth (user_id, password_hash)
                VALUES (%s, %s)
            """
            print(f'hashed password: {hashed_password}')
            self.db.cursor.execute(insert_auth_query, (user_id, hashed_password))
            self.db.conn.commit()

            s_auth_instance = _auth()
            usr = {
                'username': self.username,
                'userrole': user_role
            }
            s_auth_instance.authenticate(user_id, userinfo=usr)

            return {'status': 'success', 'message': 'User created successfully', 'status_code': 200}
        except Exception as e:
            self.db.conn.rollback() 
            print(f"Error creating user: {e}")
            return {'status': 'error', 'message': f'Error creating user: {e}', 'status_code': 500}

    def signup_user(self):
        if not self.validate_inputs():
            return {'status': 'error', 'message': 'Input validation failed', 'status_code': 400}

        try:
            duplicate_entry = self.check_duplicate_entry(
                "users",
                email=self.email,
                mobile=self.mobile,
            )
            if duplicate_entry:
                return {'status': 'error', 'message': 'Duplicate entry found', 'status_code': 409}

            return self.create_user()
        except Exception as e:
            print(f"Error during signup: {e}")
            return {'status': 'error', 'message': f'Unexpected error: {e}', 'status_code': 500}
   