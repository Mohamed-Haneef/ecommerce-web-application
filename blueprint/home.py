from flask import Blueprint, render_template, session
from lib import product
from lib import auth as _auth

home_bp = Blueprint('home_bp', __name__)

@home_bp.route('/')
def home_page():
    auth_status = _auth.is_authorized()
    if auth_status:
        name=session.get('fullname')
    else:
        name='User'
    print(session.get('user_role'))
    product_manager = product()
    products = product_manager.get_all_products() 
    return render_template('index.html', name=name, products=products, auth_status=auth_status)
