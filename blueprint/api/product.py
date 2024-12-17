from flask import Blueprint, jsonify, request, session
from lib import database  
from lib import auth as _auth
import os
from werkzeug.utils import secure_filename
import hashlib
from dotenv import load_dotenv
load_dotenv()

product_bp = Blueprint('product_api', __name__, url_prefix='/api/v1/product')

UPLOAD_FOLDER = os.getenv('PRODUCT_IMG_FOLDER') 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs('static/images/product', exist_ok=True)

static_path = 'static/images/product'

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@product_bp.route('/add', methods=['POST'])
def add_product():
    db = database()

    is_auth = _auth.is_authorized()
    if not is_auth:
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 400

    # userrole = session.get('user_role')
    # if userrole == 'customer':
    #     jsonify({'status': 'error', 'message': 'U dont have enough privileges to add a product'}), 400

    if 'product_image' not in request.files:
        return jsonify({'status': 'error', 'message': 'No image file provided'}), 400

    file = request.files['product_image']
    product_name = request.form.get('product_name')
    product_description = request.form.get('product_description')
    product_price = request.form.get('product_price')

    if not product_name or not product_description or not product_price:
        return jsonify({'status': 'error', 'message': 'Missing product details'}), 400

    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400

    try:
        filename = secure_filename(file.filename)
        unique_hash = hashlib.md5(filename.encode('utf-8')).hexdigest()
        extension = os.path.splitext(filename)[1] 
        processed_image_name = f"{unique_hash}{extension}"
        file_path = os.path.join('static/images/product/', processed_image_name)
        print(f'File path: {file_path}')
        file.save(file_path)
        processed_image_path = f"{UPLOAD_FOLDER}{processed_image_name}"
        print(f'File path on db: {processed_image_path} | upload folder path: {UPLOAD_FOLDER} | processed image name : {processed_image_name}')
        query = """
        INSERT INTO products (name, description, price, image_path) 
        VALUES (%s, %s, %s, %s)
        """
        with db.conn.cursor() as cursor:
            cursor.execute(query, (product_name, product_description, product_price, processed_image_path))
            db.conn.commit()

        return jsonify({
            'status': 'success',
            'message': 'Product added successfully',
            'data': {
                'product_name': product_name,
                'product_description': product_description,
                'product_price': product_price,
                'image_url': processed_image_path
            }
        }), 201
    
    except Exception as e:
        print(f"Error adding product: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to add product'}), 500

@product_bp.route('/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    db = database()
    is_auth = _auth.is_authorized()
    if not is_auth:
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 400

    # userrole = session.get('user_role')
    # if userrole == 'customer':
    #     jsonify({'status': 'error', 'message': 'U dont have enough privileges to add a product'}), 400


    product_name = request.form.get('product_name')
    product_description = request.form.get('product_description')
    product_price = request.form.get('product_price')
    file = request.files.get('product_image')

    if not product_name and not product_description and not product_price and not file:
        return jsonify({'status': 'error', 'message': 'No fields to update'}), 400

    try:
        update_fields = []
        update_values = []

        if product_name:
            update_fields.append("name = %s")
            update_values.append(product_name)
        
        if product_description:
            update_fields.append("description = %s")
            update_values.append(product_description)
        
        if product_price:
            update_fields.append("price = %s")
            update_values.append(product_price)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            processed_image_path = process_image(file_path) if process_image else file_path
            update_fields.append("image_path = %s")
            update_values.append(processed_image_path)

        update_values.append(product_id)

        query = f"""
        UPDATE products
        SET {', '.join(update_fields)}
        WHERE id = %s
        """

        with db.conn.cursor() as cursor:
            cursor.execute(query, update_values)
            db.conn.commit()

        return jsonify({'status': 'success', 'message': 'Product updated successfully'}), 200

    except Exception as e:
        print(f"Error updating product: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to update product'}), 500

@product_bp.route('/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    db = database()
    is_auth = _auth.is_authorized()
    if not is_auth:
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 400

    # userrole = session.get('user_role')
    # if userrole == 'customer':
    #     jsonify({'status': 'error', 'message': 'U dont have enough privileges to add a product'}), 400


    try:
        query = "DELETE FROM products WHERE id = %s"
        with db.conn.cursor() as cursor:
            cursor.execute(query, (product_id,))
            db.conn.commit()

        return jsonify({'status': 'success', 'message': 'Product deleted successfully'}), 200

    except Exception as e:
        print(f"Error deleting product: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to delete product'}), 500
