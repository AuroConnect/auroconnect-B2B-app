from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Order, OrderItem, Product, Cart, CartItem, Inventory
from app import db
from datetime import datetime, timedelta
from sqlalchemy import and_
import uuid

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def orders():
    """Get orders for the current user or create new order from cart"""
    if request.method == 'GET':
        return get_orders()
    elif request.method == 'POST':
        return create_order_from_cart()

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

@orders_bp.route('/<order_id>/status-history', methods=['GET'])
@jwt_required()
def get_order_status_history(order_id):
    """Get order status history"""
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
        
        # Parse status history from notes
        status_history = []
        if order.notes:
            lines = order.notes.split('\n')
            for line in lines:
                if line.strip().startswith('[') and 'Status changed from' in line:
                    try:
                        # Parse timestamp and status change info
                        timestamp_start = line.find('[') + 1
                        timestamp_end = line.find(']')
                        timestamp = line[timestamp_start:timestamp_end]
                        
                        # Extract status change information
                        status_info = line[timestamp_end + 1:].strip()
                        if 'Status changed from' in status_info:
                            # Extract user info
                            user_start = status_info.find('by ') + 3
                            user_end = status_info.find(':', user_start)
                            if user_end == -1:
                                user_end = len(status_info)
                            
                            updated_by = status_info[user_start:user_end].strip()
                            
                            # Extract notes if any
                            notes = ""
                            if ':' in status_info[user_end:]:
                                notes = status_info[user_end + 1:].strip()
                            
                            # Extract status change
                            status_change = status_info[:status_info.find(' by ')].strip()
                            if 'Status changed from' in status_change:
                                from_status = status_change.split(' from ')[1].split(' to ')[0]
                                to_status = status_change.split(' to ')[1]
                                
                                status_history.append({
                                    'status': to_status,
                                    'timestamp': timestamp,
                                    'notes': notes,
                                    'updatedBy': updated_by,
                                    'fromStatus': from_status
                                })
                    except Exception as e:
                        # Skip malformed lines
                        continue
        
        # Sort by timestamp (newest first)
        status_history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'orderId': order.id,
            'orderNumber': order.order_number,
            'currentStatus': order.status,
            'statusHistory': status_history
        })
        
    except Exception as e:
        return jsonify({'message': 'Failed to get status history', 'error': str(e)}), 500

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
        items = OrderItem.query.filter(OrderItem.order_id == order_id).all()
        items_with_products = []
        
        for item in items:
            product = Product.query.get(item.product_id)
            if product:
                items_with_products.append({
                    'id': item.id,
                    'productId': item.product_id,
                    'productName': product.name,
                    'productSku': product.sku,
                    'productImage': product.image_url,
                    'quantity': item.quantity,
                    'unitPrice': float(item.unit_price),
                    'totalPrice': float(item.total_price)
                })
        
        # Get retailer and distributor details
        retailer = User.query.get(order.retailer_id)
        distributor = User.query.get(order.distributor_id)
        
        # Parse status history from notes
        status_history = []
        if order.notes:
            lines = order.notes.split('\n')
            for line in lines:
                if line.strip().startswith('[') and 'Status changed from' in line:
                    try:
                        # Parse timestamp and status change info
                        timestamp_start = line.find('[') + 1
                        timestamp_end = line.find(']')
                        timestamp = line[timestamp_start:timestamp_end]
                        
                        # Extract status change information
                        status_info = line[timestamp_end + 1:].strip()
                        if 'Status changed from' in status_info:
                            # Extract user info
                            user_start = status_info.find('by ') + 3
                            user_end = status_info.find(':', user_start)
                            if user_end == -1:
                                user_end = len(status_info)
                            
                            updated_by = status_info[user_start:user_end].strip()
                            
                            # Extract notes if any
                            notes = ""
                            if ':' in status_info[user_end:]:
                                notes = status_info[user_end + 1:].strip()
                            
                            # Extract status change
                            status_change = status_info[:status_info.find(' by ')].strip()
                            if 'Status changed from' in status_change:
                                from_status = status_change.split(' from ')[1].split(' to ')[0]
                                to_status = status_change.split(' to ')[1]
                                
                                status_history.append({
                                    'status': to_status,
                                    'timestamp': timestamp,
                                    'notes': notes,
                                    'updatedBy': updated_by,
                                    'fromStatus': from_status
                                })
                    except Exception as e:
                        # Skip malformed lines
                        continue
        
        # Sort by timestamp (newest first)
        status_history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        order_details = {
            'id': order.id,
            'orderNumber': order.order_number,
            'status': order.status,
            'deliveryMode': order.delivery_mode,
            'totalAmount': float(order.total_amount),
            'notes': order.notes,
            'createdAt': order.created_at.isoformat(),
            'updatedAt': order.updated_at.isoformat(),
            'retailer': {
                'id': retailer.id,
                'name': f"{retailer.first_name} {retailer.last_name}",
                'email': retailer.email,
                'phone': retailer.phone_number
            } if retailer else None,
            'distributor': {
                'id': distributor.id,
                'name': f"{distributor.first_name} {distributor.last_name}",
                'email': distributor.email,
                'phone': distributor.phone_number
            } if distributor else None,
            'items': items_with_products,
            'statusHistory': status_history
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
        notes = data.get('notes', '')
        
        if not new_status:
            return jsonify({'message': 'Status is required'}), 400
        
        # Enhanced status validation with flow logic
        valid_statuses = ['pending', 'confirmed', 'accepted', 'processing', 'packed', 'shipped', 'out_for_delivery', 'delivered', 'cancelled', 'rejected']
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
        
        # Status flow validation
        current_status = order.status
        valid_transitions = {
            'pending': ['confirmed', 'accepted', 'rejected', 'cancelled'],
            'confirmed': ['accepted', 'processing', 'rejected', 'cancelled'],
            'accepted': ['processing', 'packed', 'rejected', 'cancelled'],
            'processing': ['packed', 'shipped', 'rejected', 'cancelled'],
            'packed': ['shipped', 'out_for_delivery', 'rejected', 'cancelled'],
            'shipped': ['out_for_delivery', 'delivered', 'rejected', 'cancelled'],
            'out_for_delivery': ['delivered', 'rejected', 'cancelled'],
            'delivered': [],  # Final state
            'rejected': [],   # Final state
            'cancelled': []   # Final state
        }
        
        if current_status in valid_transitions and new_status not in valid_transitions[current_status]:
            return jsonify({
                'message': f'Invalid status transition from {current_status} to {new_status}',
                'validTransitions': valid_transitions[current_status]
            }), 400
        
        # Prevent updating final states
        if current_status in ['delivered', 'rejected', 'cancelled']:
            return jsonify({'message': f'Cannot update order status from {current_status}'}), 400
        
        # Store previous status for history
        previous_status = order.status
        
        # Update order status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # Enhanced notes handling with timestamp and user info
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        user_info = f"{user.first_name} {user.last_name} ({user.role})"
        
        if notes:
            status_note = f"[{timestamp}] Status changed from {previous_status} to {new_status} by {user_info}: {notes}"
        else:
            status_note = f"[{timestamp}] Status changed from {previous_status} to {new_status} by {user_info}"
        
        # Append to existing notes or create new notes
        if order.notes:
            order.notes = f"{order.notes}\n{status_note}"
        else:
            order.notes = status_note
        
        # Handle inventory updates for certain status changes
        if new_status == 'shipped' and previous_status != 'shipped':
            # Update inventory when order is shipped
            order_items = OrderItem.query.filter(OrderItem.order_id == order_id).all()
            for item in order_items:
                # Find inventory for this product and distributor
                inventory = Inventory.query.filter_by(
                    distributor_id=order.distributor_id,
                    product_id=item.product_id
                ).first()
                
                if inventory and inventory.quantity >= item.quantity:
                    inventory.quantity -= item.quantity
                elif inventory:
                    # If insufficient stock, mark as partial shipment
                    inventory.quantity = 0
                    # You might want to add a note about partial shipment
        
        db.session.commit()
        
        # Return enhanced response with status history
        return jsonify({
            'message': 'Order status updated successfully',
            'orderId': order.id,
            'orderNumber': order.order_number,
            'previousStatus': previous_status,
            'newStatus': new_status,
            'updatedAt': order.updated_at.isoformat(),
            'updatedBy': user_info,
            'notes': notes
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update order status', 'error': str(e)}), 500

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

def create_order_from_cart():
    """Create order from user's cart"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Only retailers and distributors can place orders
        if user.role not in ['retailer', 'distributor']:
            return jsonify({'message': 'Only retailers and distributors can place orders'}), 403
        
        # Get user's cart
        cart = Cart.query.filter_by(user_id=current_user_id).first()
        if not cart:
            return jsonify({'message': 'Cart is empty'}), 400
        
        # Get cart items
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
        if not cart_items:
            return jsonify({'message': 'Cart is empty'}), 400
        
        # Validate cart items and determine target partner
        target_partner_id = None
        total_amount = 0.0
        order_items_data = []
        
        for cart_item in cart_items:
            product = Product.query.get(cart_item.product_id)
            if not product:
                return jsonify({'message': f'Product {cart_item.product_id} not found'}), 404
            
            # Determine target partner based on user role and product
            if user.role == 'retailer':
                # Retailer orders from distributor - need to find which distributor has this product
                # For now, we'll use the product's manufacturer as the distributor
                # In a real scenario, you'd check the inventory table
                if not target_partner_id:
                    target_partner_id = product.manufacturer_id
                elif target_partner_id != product.manufacturer_id:
                    return jsonify({'message': 'All products must be from the same distributor'}), 400
            elif user.role == 'distributor':
                # Distributor orders from manufacturer
                if not target_partner_id:
                    target_partner_id = product.manufacturer_id
                elif target_partner_id != product.manufacturer_id:
                    return jsonify({'message': 'All products must be from the same manufacturer'}), 400
            
            # Calculate item total
            unit_price = float(product.base_price) if product.base_price else 0.0  # Convert to float
            item_total = unit_price * cart_item.quantity
            total_amount += item_total
            
            order_items_data.append({
                'product_id': cart_item.product_id,
                'quantity': cart_item.quantity,
                'unit_price': unit_price,
                'total_price': item_total
            })
        
        if not target_partner_id:
            return jsonify({'message': 'Unable to determine target partner'}), 400
        
        # Create order
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        order = Order(
            id=str(uuid.uuid4()),
            order_number=order_number,
            retailer_id=current_user_id if user.role == 'retailer' else target_partner_id,
            distributor_id=target_partner_id if user.role == 'retailer' else current_user_id,
            status='pending',
            delivery_mode='delivery',
            total_amount=total_amount,
            notes=f"Order placed from cart by {user.first_name} {user.last_name}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order items
        for item_data in order_items_data:
            order_item = OrderItem(
                id=str(uuid.uuid4()),
                order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )
            db.session.add(order_item)
        
        # Clear the cart
        CartItem.query.filter_by(cart_id=cart.id).delete()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'orderId': order.id,
            'orderNumber': order.order_number,
            'totalAmount': float(total_amount),
            'itemsCount': len(order_items_data)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create order', 'error': str(e)}), 500 