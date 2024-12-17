from lib.utils.database import database
from lib.core.auth import auth

class product:
    def __init__(self):
        self.db = database()

    def get_all_products(self):
        """Fetch all products from the database."""
        query = "SELECT id, name, description, price, image_path FROM products"
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                products = [dict(zip(columns, row)) for row in rows]
            return products
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []

    def get_product_by_id(self, product_id):
        try:
            query = "SELECT id, name, description, price, image_path FROM products WHERE id = %s;"
            with self.db.conn.cursor() as cursor:
                cursor.execute(query, (product_id,))
                product = cursor.fetchone()  # Fetch single product based on ID
                if product:
                    return {
                        'id': product[0],
                        'name': product[1],
                        'description': product[2],
                        'price': product[3],
                        'image_path': product[4]
                    }
                return None
        except Exception as e:
            print(f"Error fetching product by ID: {e}")
            return None
        