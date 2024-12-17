from lib.utils.database import database

class cart:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = database()

    def add_item(self, product_id, quantity):
        query = """
        INSERT INTO cart (user_id, product_id, quantity)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, product_id) DO UPDATE 
        SET quantity = cart.quantity + EXCLUDED.quantity
        """
        with self.db.conn.cursor() as cursor:
            cursor.execute(query, (self.user_id, product_id, quantity))
            self.db.conn.commit()

    def update_item(self, product_id, quantity):
        query = "UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s"
        with self.db.conn.cursor() as cursor:
            cursor.execute(query, (quantity, self.user_id, product_id))
            self.db.conn.commit()

    def remove_item(self, product_id):
        query = "DELETE FROM cart WHERE user_id = %s AND product_id = %s"
        with self.db.conn.cursor() as cursor:
            cursor.execute(query, (self.user_id, product_id))
            self.db.conn.commit()

    def clear_cart(self):
        query = "DELETE FROM cart WHERE user_id = %s"
        with self.db.conn.cursor() as cursor:
            cursor.execute(query, (self.user_id,))
            self.db.conn.commit()

    def get_cart_items(self):
        query = """
        SELECT p.id, p.name, p.price, c.quantity 
        FROM products p
        JOIN cart c ON p.id = c.product_id
        WHERE c.user_id = %s
        """
        with self.db.conn.cursor() as cursor:
            cursor.execute(query, (self.user_id,))
            return cursor.fetchall()
