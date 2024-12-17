from flask import Blueprint, request, jsonify, session
from lib import cart as _cart
from lib import database
from lib import auth as _auth

cart_bp = Blueprint('cart_api', __name__, url_prefix='/api/v1/cart')

@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    try:

        is_auth = _auth.is_authorized()
        user_id = session.get('user_id')
        if not is_auth:
            return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401

        product_id = request.json.get('product_id')
        quantity = request.json.get('quantity', 1)

        if not product_id or quantity <= 0:
            return jsonify({'status': 'error', 'message': 'Invalid product or quantity'}), 400

        cart = _cart(user_id)
        cart.add_item(product_id, quantity)

        return jsonify({'status': 'success', 'message': 'Product added to cart'}), 200
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to add product to cart'}), 500

@cart_bp.route('/update', methods=['PUT'])
def update_cart():
    try:
        is_auth = _auth.is_authorized()
        user_id = session.get('user_id')
        if not is_auth:
            return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401

        product_id = request.json.get('product_id')
        quantity = request.json.get('quantity')

        if not product_id or quantity <= 0:
            return jsonify({'status': 'error', 'message': 'Invalid product or quantity'}), 400

        cart = _cart(user_id)
        cart.update_item(product_id, quantity)

        return jsonify({'status': 'success', 'message': 'Cart updated successfully'}), 200
    except Exception as e:
        print(f"Error updating cart: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to update cart'}), 500

@cart_bp.route('/remove', methods=['DELETE'])
def remove_from_cart():
    try:
        is_auth = _auth.is_authorized()
        user_id = session.get('user_id')
        if not is_auth:
            return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401

        product_id = request.json.get('product_id')

        if not product_id:
            return jsonify({'status': 'error', 'message': 'Invalid product'}), 400

        cart = _cart(user_id)
        cart.remove_item(product_id)

        return jsonify({'status': 'success', 'message': 'Product removed from cart'}), 200
    except Exception as e:
        print(f"Error removing from cart: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to remove product from cart'}), 500

@cart_bp.route('/clear', methods=['DELETE'])
def clear_cart():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401

        cart = _cart(user_id)
        cart.clear_cart()

        return jsonify({'status': 'success', 'message': 'Cart cleared successfully'}), 200
    except Exception as e:
        print(f"Error clearing cart: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to clear cart'}), 500
