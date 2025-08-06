from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Order, OrderItem, Product
from app import db
from datetime import datetime, timedelta
from sqlalchemy import and_

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """Get orders for the current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get query parameters
        status_filter = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build query based on user role
        if user.role == 'retailer':
            query = Order.query.filter(Order.retailer_id == current_user_id)
        elif user.role == 'distributor':
            query = Order.query.filter(Order.distributor_id == current_user_id)
        elif user.role == 'manufacturer':
            # Manufacturers see orders for their products
            query = Order.query.join(OrderItem).join(Product).filter(
                Product.manufacturer_id == current_user_id
            ).distinct()
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        # Apply filters
        if status_filter:
            query = query.filter(Order.status == status_filter)
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Order.created_at >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Order.created_at < date_to_obj)
            except ValueError:
                pass
        
        # Order by creation date
        query = query.order_by(Order.created_at.desc())
        
        orders = query.all()
        
        # Format orders with details
        formatted_orders = []
        for order in orders:
            # Get order items with product details
            order_items = OrderItem.query.filter(OrderItem.order_id == order.id).all()
            items_with_products = []
            
            for item in order_items:
                product = Product.query.get(item.product_id)
                items_with_products.append({
                    'id': item.id,
                    'productId': item.product_id,
                    'productName': product.name if product else 'Unknown Product',
                    'productSku': product.sku if product else '',
                    'quantity': item.quantity,
                    'unitPrice': float(item.unit_price),
                    'totalPrice': float(item.total_price),
                    'productImage': product.image_url if product else None
                })
            
            # Get retailer and distributor details
            retailer = User.query.get(order.retailer_id)
            distributor = User.query.get(order.distributor_id)
            
            formatted_orders.append({
                'id': order.id,
                'orderNumber': order.order_number,
                'status': order.status,
                'totalAmount': float(order.total_amount),
                'notes': order.notes,
                'createdAt': order.created_at.isoformat(),
                'updatedAt': order.updated_at.isoformat(),
                'retailer': {
                    'id': retailer.id,
                    'name': retailer.business_name or f"{retailer.first_name} {retailer.last_name}",
                    'email': retailer.email
                } if retailer else None,
                'distributor': {
                    'id': distributor.id,
                    'name': distributor.business_name or f"{distributor.first_name} {distributor.last_name}",
                    'email': distributor.email
                } if distributor else None,
                'items': items_with_products
            })
        
        return jsonify(formatted_orders)
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@orders_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order_details(order_id):
    """Get detailed order information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user has access to this order
        if user.role == 'retailer' and order.retailer_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'distributor' and order.distributor_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'manufacturer':
            # Check if any products in the order belong to this manufacturer
            order_items = OrderItem.query.filter(OrderItem.order_id == order_id).all()
            product_ids = [item.product_id for item in order_items]
            manufacturer_products = Product.query.filter(
                and_(Product.id.in_(product_ids), Product.manufacturer_id == current_user_id)
            ).count()
            if manufacturer_products == 0:
                return jsonify({'message': 'Access denied'}), 403
        
        # Get order items with product details
        order_items = OrderItem.query.filter(OrderItem.order_id == order_id).all()
        items_with_products = []
        
        for item in order_items:
            product = Product.query.get(item.product_id)
            items_with_products.append({
                'id': item.id,
                'productId': item.product_id,
                'productName': product.name if product else 'Unknown Product',
                'productSku': product.sku if product else '',
                'quantity': item.quantity,
                'unitPrice': float(item.unit_price),
                'totalPrice': float(item.total_price),
                'productImage': product.image_url if product else None,
                'productDescription': product.description if product else ''
            })
        
        # Get retailer and distributor details
        retailer = User.query.get(order.retailer_id)
        distributor = User.query.get(order.distributor_id)
        
        order_details = {
            'id': order.id,
            'orderNumber': order.order_number,
            'status': order.status,
            'totalAmount': float(order.total_amount),
            'notes': order.notes,
            'createdAt': order.created_at.isoformat(),
            'updatedAt': order.updated_at.isoformat(),
            'retailer': {
                'id': retailer.id,
                'name': retailer.business_name or f"{retailer.first_name} {retailer.last_name}",
                'email': retailer.email,
                'phone': retailer.phone_number
            } if retailer else None,
            'distributor': {
                'id': distributor.id,
                'name': distributor.business_name or f"{distributor.first_name} {distributor.last_name}",
                'email': distributor.email,
                'phone': distributor.phone_number
            } if distributor else None,
            'items': items_with_products
        }
        
        return jsonify(order_details)
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@orders_bp.route('/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """Update order status (for distributors and manufacturers)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if user.role not in ['distributor', 'manufacturer']:
            return jsonify({'message': 'Only distributors and manufacturers can update order status'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'message': 'Status is required'}), 400
        
        valid_statuses = ['pending', 'accepted', 'rejected', 'processing', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user has access to this order
        if user.role == 'distributor' and order.distributor_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'manufacturer':
            # Check if any products in the order belong to this manufacturer
            order_items = OrderItem.query.filter(OrderItem.order_id == order_id).all()
            product_ids = [item.product_id for item in order_items]
            manufacturer_products = Product.query.filter(
                and_(Product.id.in_(product_ids), Product.manufacturer_id == current_user_id)
            ).count()
            if manufacturer_products == 0:
                return jsonify({'message': 'Access denied'}), 403
        
        # Update order status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # Add notes if provided
        if data.get('notes'):
            order.notes = f"{order.notes or ''}\n{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}: {data['notes']}"
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order status updated successfully',
            'orderId': order.id,
            'newStatus': new_status
        })
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@orders_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_order_stats():
    """Get order statistics for the current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Build query based on user role
        if user.role == 'retailer':
            base_query = Order.query.filter(Order.retailer_id == current_user_id)
        elif user.role == 'distributor':
            base_query = Order.query.filter(Order.distributor_id == current_user_id)
        elif user.role == 'manufacturer':
            base_query = Order.query.join(OrderItem).join(Product).filter(
                Product.manufacturer_id == current_user_id
            ).distinct()
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        # Get total orders
        total_orders = base_query.count()
        
        # Get orders by status
        status_counts = {}
        for status in ['pending', 'accepted', 'rejected', 'processing', 'shipped', 'delivered', 'cancelled']:
            count = base_query.filter(Order.status == status).count()
            status_counts[status] = count
        
        # Get total revenue
        total_revenue = base_query.filter(Order.status.in_(['delivered', 'shipped'])).with_entities(
            db.func.sum(Order.total_amount)
        ).scalar() or 0
        
        # Get recent orders (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_orders = base_query.filter(Order.created_at >= thirty_days_ago).count()
        
        # Get monthly revenue
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = base_query.filter(
            and_(Order.status.in_(['delivered', 'shipped']), Order.created_at >= current_month_start)
        ).with_entities(db.func.sum(Order.total_amount)).scalar() or 0
        
        stats = {
            'totalOrders': total_orders,
            'totalRevenue': float(total_revenue),
            'monthlyRevenue': float(monthly_revenue),
            'recentOrders': recent_orders,
            'statusBreakdown': status_counts
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500 