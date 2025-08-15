from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Order, OrderItem, Product, ProductAllocation
from app.utils.decorators import role_required
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
import calendar

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get analytics stats for current user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get current month and last month dates
        now = datetime.utcnow()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        # Calculate stats based on user role
        if current_user.role == 'manufacturer':
            # Manufacturer stats - manufacturers don't have direct orders in this schema
            # They sell to distributors who then sell to retailers
            current_month_orders = 0
            last_month_orders = 0
            
            current_month_revenue = 0
            last_month_revenue = 0
            
            total_products = Product.query.filter_by(manufacturer_id=current_user_id, is_active=True).count()
            
            active_distributors = db.session.query(func.count(func.distinct(ProductAllocation.distributor_id))).filter(
                and_(
                    ProductAllocation.manufacturer_id == current_user_id,
                    ProductAllocation.is_active == True
                )
            ).scalar() or 0
            
            # Calculate trends
            order_trend = ((current_month_orders - last_month_orders) / max(last_month_orders, 1)) * 100 if last_month_orders > 0 else 0
            revenue_trend = ((current_month_revenue - last_month_revenue) / max(last_month_revenue, 1)) * 100 if last_month_revenue > 0 else 0
            
            stats = {
                'totalOrders': current_month_orders,
                'totalRevenue': float(current_month_revenue),
                'productsCount': total_products,
                'activePartners': active_distributors,
                'orderTrend': round(order_trend, 1),
                'revenueTrend': round(revenue_trend, 1),
                'currentMonth': now.strftime('%B %Y'),
                'lastMonth': last_month_start.strftime('%B %Y')
            }
            
        elif current_user.role == 'distributor':
            # Distributor stats
            current_month_orders = Order.query.filter(
                and_(
                    Order.distributor_id == current_user_id,
                    Order.created_at >= current_month_start
                )
            ).count()
            
            last_month_orders = Order.query.filter(
                and_(
                    Order.distributor_id == current_user_id,
                    Order.created_at >= last_month_start,
                    Order.created_at < current_month_start
                )
            ).count()
            
            current_month_revenue = db.session.query(func.sum(OrderItem.quantity * OrderItem.unit_price)).join(Order).filter(
                and_(
                    Order.distributor_id == current_user_id,
                    Order.created_at >= current_month_start,
                    Order.status.in_(['completed', 'delivered'])
                )
            ).scalar() or 0
            
            last_month_revenue = db.session.query(func.sum(OrderItem.quantity * OrderItem.unit_price)).join(Order).filter(
                and_(
                    Order.distributor_id == current_user_id,
                    Order.created_at >= last_month_start,
                    Order.created_at < current_month_start,
                    Order.status.in_(['completed', 'delivered'])
                )
            ).scalar() or 0
            
            # Count products in inventory
            total_products = db.session.query(func.count(func.distinct(Product.id))).join(ProductAllocation).filter(
                and_(
                    ProductAllocation.distributor_id == current_user_id,
                    ProductAllocation.is_active == True,
                    Product.is_active == True
                )
            ).scalar() or 0
            
            # Count active retailers (those who have placed orders)
            active_retailers = db.session.query(func.count(func.distinct(Order.retailer_id))).filter(
                and_(
                    Order.distributor_id == current_user_id,
                    Order.created_at >= current_month_start
                )
            ).scalar() or 0
            
            # Calculate trends
            order_trend = ((current_month_orders - last_month_orders) / max(last_month_orders, 1)) * 100 if last_month_orders > 0 else 0
            revenue_trend = ((current_month_revenue - last_month_revenue) / max(last_month_revenue, 1)) * 100 if last_month_revenue > 0 else 0
            
            stats = {
                'totalOrders': current_month_orders,
                'totalRevenue': float(current_month_revenue),
                'productsCount': total_products,
                'activeRetailers': active_retailers,
                'orderTrend': round(order_trend, 1),
                'revenueTrend': round(revenue_trend, 1),
                'currentMonth': now.strftime('%B %Y'),
                'lastMonth': last_month_start.strftime('%B %Y')
            }
            
        else:
            # Retailer stats
            current_month_orders = Order.query.filter(
                and_(
                    Order.retailer_id == current_user_id,
                    Order.created_at >= current_month_start
                )
            ).count()
            
            last_month_orders = Order.query.filter(
                and_(
                    Order.retailer_id == current_user_id,
                    Order.created_at >= last_month_start,
                    Order.created_at < current_month_start
                )
            ).count()
            
            current_month_revenue = db.session.query(func.sum(OrderItem.quantity * OrderItem.unit_price)).join(Order).filter(
                and_(
                    Order.retailer_id == current_user_id,
                    Order.created_at >= current_month_start,
                    Order.status.in_(['completed', 'delivered'])
                )
            ).scalar() or 0
            
            last_month_revenue = db.session.query(func.sum(OrderItem.quantity * OrderItem.unit_price)).join(Order).filter(
                and_(
                    Order.retailer_id == current_user_id,
                    Order.created_at >= last_month_start,
                    Order.created_at < current_month_start,
                    Order.status.in_(['completed', 'delivered'])
                )
            ).scalar() or 0
            
            pending_orders = Order.query.filter(
                and_(
                    Order.retailer_id == current_user_id,
                    Order.status.in_(['pending', 'accepted'])
                )
            ).count()
            
            # Calculate trends
            order_trend = ((current_month_orders - last_month_orders) / max(last_month_orders, 1)) * 100 if last_month_orders > 0 else 0
            revenue_trend = ((current_month_revenue - last_month_revenue) / max(last_month_revenue, 1)) * 100 if last_month_revenue > 0 else 0
            
            stats = {
                'totalOrders': current_month_orders,
                'totalRevenue': float(current_month_revenue),
                'pendingOrders': pending_orders,
                'orderTrend': round(order_trend, 1),
                'revenueTrend': round(revenue_trend, 1),
                'currentMonth': now.strftime('%B %Y'),
                'lastMonth': last_month_start.strftime('%B %Y')
            }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch analytics: {str(e)}'}), 500 