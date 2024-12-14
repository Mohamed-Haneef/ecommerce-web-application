from lib.utils.database import database

class user:
    def __init__(self):
        self.db = database()
    

def find_user_by_email(self, email):
    try:
        query = "SELECT * FROM User WHERE email = %s;"  
        cursor = self.db.conn.cursor()
        cursor.execute(query, (email,))
        user = cursor.fetchone()  
        return user.id
    except Exception as e:
        print(f"Error finding user by email: {e}")
        return None