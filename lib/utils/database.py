import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

class database:
    def __init__(self):
        self.db_user = os.getenv('DB_USER')
        self.db_pass = os.getenv('DB_PASS')
        self.db_host = os.getenv('DB_HOST')
        self.db_port = os.getenv('DB_PORT')
        self.db_name = os.getenv('DB_NAME')
        self.conn = psycopg2.connect(
            database=self.db_name,
            user=self.db_user,
            password=self.db_pass,
            host=self.db_host,
            port=self.db_port
        )
        self.cursor = self.conn.cursor()

    def get_cursor(self):
        return self.cursor

    def close_connection(self):
        self.cursor.close()
        self.conn.close()