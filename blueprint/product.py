from flask import Blueprint, render_template, session, request, redirect, url_for
from lib import product as _product
from lib import auth as _auth

product_bp = Blueprint('product_bp', __name__, url_prefix='/product')

@product_bp.route('/add')
def add_product():
    is_auth = _auth.is_authorized()
    if not is_auth:
        return redirect(url_for('auth.login'))

    # userrole = session.get('user_role')
    # if userrole == 'customer':
    #     jsonify({'status': 'error', 'message': 'U dont have enough privileges to add a product'}), 400


    return render_template('add_product.html', auth_status=is_auth)

@product_bp.route('/view/<int:product_id>')
def view_product(product_id):
    is_auth = _auth.is_authorized()
    if not is_auth:
        return redirect(url_for('auth.login'))

    product_manager = _product()
    product_info = product_manager.get_product_by_id(product_id)

    if not product_info:
        return render_template('404.html'), 404 

    return render_template('view_product.html', product=product_info, auth_status=is_auth)