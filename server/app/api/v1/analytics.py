from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Order, Product, OrderItem
from app import db
from datetime import datetime, timedelta
import random

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
            'totalOrders': 0,
            'totalRevenue': 0,
            'pendingOrders': 0,
            'completedOrders': 0,
            'productsCount': 0,
            'activePartners': 0,
            'productionVolume': 0
        }
        
        if user.role == 'retailer':
            # For retailers, get their orders
            orders = Order.query.filter_by(retailer_id=current_user_id).all()
            stats['totalOrders'] = len(orders)
            stats['totalRevenue'] = sum(order.total_amount or 0 for order in orders)
            stats['pendingOrders'] = len([o for o in orders if o.status == 'pending'])
            stats['completedOrders'] = len([o for o in orders if o.status == 'delivered'])
            
        elif user.role == 'distributor':
            # For distributors, get orders they're fulfilling
            orders = Order.query.filter_by(distributor_id=current_user_id).all()
            stats['totalOrders'] = len(orders)
            stats['pendingOrders'] = len([o for o in orders if o.status == 'pending'])
            stats['completedOrders'] = len([o for o in orders if o.status == 'delivered'])
            
        elif user.role == 'manufacturer':
            # For manufacturers, get their products and related orders
            products = Product.query.filter_by(manufacturer_id=current_user_id).all()
            stats['productsCount'] = len(products)
            
            # Get orders for manufacturer's products
            manufacturer_orders = Order.query.join(OrderItem).join(Product).filter(
                Product.manufacturer_id == current_user_id
            ).all()
            
            stats['totalOrders'] = len(manufacturer_orders)
            stats['totalRevenue'] = sum(order.total_amount or 0 for order in manufacturer_orders)
            stats['pendingOrders'] = len([o for o in manufacturer_orders if o.status == 'pending'])
            stats['completedOrders'] = len([o for o in manufacturer_orders if o.status == 'delivered'])
            
            # Calculate production volume (simulated data for demo)
            if stats['productsCount'] > 0:
                # Simulate production volume based on products and orders
                base_volume = stats['productsCount'] * 250  # Base volume per product
                order_volume = stats['totalOrders'] * 50    # Volume from orders
                stats['productionVolume'] = base_volume + order_volume + random.randint(100, 500)
            else:
                stats['productionVolume'] = 1250  # Default demo value
            
            # Count active partners (distributors who have ordered manufacturer's products)
            active_partners = db.session.query(Order.distributor_id).join(OrderItem).join(Product).filter(
                Product.manufacturer_id == current_user_id
            ).distinct().count()
            stats['activePartners'] = active_partners
            
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'message': 'Error fetching stats', 'error': str(e)}), 500 