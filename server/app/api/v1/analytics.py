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
            # For retailers, get their orders (as buyers)
            orders = Order.query.filter_by(buyer_id=current_user_id).all()
            stats['totalOrders'] = len(orders)
            stats['totalRevenue'] = sum(order.total_amount or 0 for order in orders)
            stats['pendingOrders'] = len([o for o in orders if o.status == 'pending'])
            stats['completedOrders'] = len([o for o in orders if o.status == 'delivered'])
            
        elif user.role == 'distributor':
            # For distributors, get orders they're fulfilling (as sellers)
            orders = Order.query.filter_by(seller_id=current_user_id).all()
            stats['totalOrders'] = len(orders)
            stats['pendingOrders'] = len([o for o in orders if o.status == 'pending'])
            stats['completedOrders'] = len([o for o in orders if o.status == 'delivered'])
            
        elif user.role == 'manufacturer':
            # For manufacturers, get their products and related orders
            products = Product.query.filter_by(created_by=current_user_id).all()
            stats['productsCount'] = len(products)
            
            # Get orders for manufacturer's products
            manufacturer_orders = Order.query.join(Product).filter(
                Product.created_by == current_user_id
            ).all()
            
            stats['totalOrders'] = len(manufacturer_orders)
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
            active_partners = db.session.query(Order.buyer_id).join(Product).filter(
                Product.created_by == current_user_id
            ).distinct().count()
            stats['activePartners'] = active_partners
            
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'message': 'Error fetching stats', 'error': str(e)}), 500

@analytics_bp.route('/manufacturer-stats', methods=['GET'])
@jwt_required()
def get_manufacturer_stats():
    """Get manufacturer-specific analytics stats"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'manufacturer':
            return jsonify({'message': 'Access denied'}), 403
        
        # Get manufacturer's products
        products = Product.query.filter_by(created_by=current_user_id).all()
        total_products = len(products)
        
        # Get orders for manufacturer's products
        orders = Order.query.join(Product).filter(
            Product.created_by == current_user_id
        ).all()
        
        pending_orders = len([o for o in orders if o.status == 'pending'])
        
        # Count invoices generated
        invoices_generated = len([o for o in orders if o.invoice_path])
        
        return jsonify({
            'totalProducts': total_products,
            'pendingOrders': pending_orders,
            'invoicesGenerated': invoices_generated,
            'totalOrders': len(orders)
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error fetching manufacturer stats', 'error': str(e)}), 500

@analytics_bp.route('/distributor-stats', methods=['GET'])
@jwt_required()
def get_distributor_stats():
    """Get distributor-specific analytics stats"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'distributor':
            return jsonify({'message': 'Access denied'}), 403
        
        # Get orders where distributor is seller
        orders = Order.query.filter_by(seller_id=current_user_id).all()
        pending_orders = len([o for o in orders if o.status == 'pending'])
        
        # Calculate monthly sales (simulated)
        monthly_sales = sum(float(o.product.price) * o.quantity for o in orders if o.status == 'delivered')
        
        return jsonify({
            'pendingOrders': pending_orders,
            'monthlySales': round(monthly_sales, 2),
            'totalOrders': len(orders)
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error fetching distributor stats', 'error': str(e)}), 500

@analytics_bp.route('/retailer-stats', methods=['GET'])
@jwt_required()
def get_retailer_stats():
    """Get retailer-specific analytics stats"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'retailer':
            return jsonify({'message': 'Access denied'}), 403
        
        # Get retailer's orders
        orders = Order.query.filter_by(buyer_id=current_user_id).all()
        pending_orders = len([o for o in orders if o.status == 'pending'])
        
        return jsonify({
            'totalOrders': len(orders),
            'pendingOrders': pending_orders
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Error fetching retailer stats', 'error': str(e)}), 500 