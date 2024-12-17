from flask import Blueprint, render_template, session, redirect, url_for
from lib import cart as _cart
from lib import auth as _auth

cart_view_bp = Blueprint('cart_view_bp', __name__)

@cart_view_bp.route('/cart')
def view_cart():
    is_auth = _auth.is_authorized()
    user_id = session.get('user_id')
    
    if not is_auth:
        return redirect(url_for('auth.login'))

    cart = _cart(user_id)
    items = cart.get_cart_items()

    total = sum(item[2] * item[3] for item in items)  # item[2] is price, item[3] is quantity

    return render_template('cart.html', items=items, total=total, auth_status=is_auth)
