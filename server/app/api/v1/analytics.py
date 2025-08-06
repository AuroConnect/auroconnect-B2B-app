from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Order, Product
from app import db

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get analytics stats for the current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get basic stats based on user role
        stats = {
            'total_orders': 0,
            'total_revenue': 0,
            'pending_orders': 0,
            'completed_orders': 0,
            'total_products': 0,
            'active_partners': 0
        }
        
        if user.role == 'retailer':
            # For retailers, get their orders
            orders = Order.query.filter_by(retailer_id=current_user_id).all()
            stats['total_orders'] = len(orders)
            stats['total_revenue'] = sum(order.total_amount or 0 for order in orders)
            stats['pending_orders'] = len([o for o in orders if o.status == 'pending'])
            stats['completed_orders'] = len([o for o in orders if o.status == 'delivered'])
            
        elif user.role == 'distributor':
            # For distributors, get orders they're fulfilling
            orders = Order.query.filter_by(distributor_id=current_user_id).all()
            stats['total_orders'] = len(orders)
            stats['pending_orders'] = len([o for o in orders if o.status == 'pending'])
            stats['completed_orders'] = len([o for o in orders if o.status == 'delivered'])
            
        elif user.role == 'manufacturer':
            # For manufacturers, get their products
            products = Product.query.filter_by(manufacturer_id=current_user_id).all()
            stats['total_products'] = len(products)
            
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'message': 'Error fetching stats', 'error': str(e)}), 500 