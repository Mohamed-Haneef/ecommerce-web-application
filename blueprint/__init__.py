from .auth import auth_bp
from .oauth import oauth_bp
from .api.product import product_bp
from .api.user import user_bp
from .product import product_bp as standalone_product_bp
from .user import user_bp as standalone_user_bp
from .home import home_bp as home_bp
from .cart import cart_view_bp as standalone_cart_bp
from .api.cart import cart_bp as cart_bp
from .images import image_bp

def init_app(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(standalone_cart_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(standalone_product_bp)
    app.register_blueprint(standalone_user_bp)