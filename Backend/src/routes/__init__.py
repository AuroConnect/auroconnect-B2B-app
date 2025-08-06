from .auth import auth_bp
from .manufacturer import manufacturer_bp
from .distributor import distributor_bp
from .retailer import retailer_bp
from .api import api_bp

__all__ = [
    'auth_bp',
    'manufacturer_bp',
    'distributor_bp',
    'retailer_bp',
    'api_bp'
]