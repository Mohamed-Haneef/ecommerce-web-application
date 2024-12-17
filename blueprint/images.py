from flask import Blueprint, send_from_directory

image_bp = Blueprint('image', __name__)

# Serve product images
@image_bp.route('/images/product/<path:filename>')
def serve_product(filename):
    return send_from_directory('static/images/product', filename)

# Serve user profile images
@image_bp.route('/images/user/<path:filename>')
def serve_user(filename):
    return send_from_directory('static/images/user', filename)
