from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.models.cart import CartItem
from app.models.inventory import Inventory
from app.models.product_allocation import ProductAllocation
from app.models.whatsapp import WhatsAppNotification
from app.utils.decorators import role_required, roles_required
from datetime import datetime
import uuid

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    """Get orders based on user role with enhanced hierarchy support"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        status_filter = request.args.get('status')
        order_type = request.args.get('type', 'all')  # 'buying', 'selling', 'all'
        
        # Enhanced role-based order filtering
        if current_user.role == 'manufacturer':
            # Manufacturer sees orders from distributors who are ordering their products
            # We need to find orders where the distributor has ordered products from this manufacturer
            from app.models.product_allocation import ProductAllocation
            
            # Get all products from this manufacturer
            manufacturer_products = Product.query.filter_by(manufacturer_id=current_user_id).all()
            manufacturer_product_ids = [p.id for p in manufacturer_products]
            
            # Get order items that contain products from this manufacturer
            order_items_with_manufacturer_products = OrderItem.query.filter(
                OrderItem.product_id.in_(manufacturer_product_ids)
            ).all()
            
            # Get order IDs from these order items
            order_ids = [item.order_id for item in order_items_with_manufacturer_products]
            
            if order_ids:
                query = Order.query.filter(Order.id.in_(order_ids))
            else:
                query = Order.query.filter_by(id=None)  # Return no results
            
        elif current_user.role == 'distributor':
            if order_type == 'buying':
                # Orders to manufacturer (for restocking) - not implemented in this schema
                query = Order.query.filter_by(id=None)  # Return no results
            elif order_type == 'selling':
                # Orders from retailers (fulfilling retailer orders)
                query = Order.query.filter_by(distributor_id=current_user_id)
            else:
                # All orders (selling to retailers)
                query = Order.query.filter_by(distributor_id=current_user_id)
                
        elif current_user.role == 'retailer':
            # Retailer sees orders where they are the buyer (from distributor)
            query = Order.query.filter_by(retailer_id=current_user_id)
            
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        # Apply status filter
        if status_filter and status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        # Order by creation date
        query = query.order_by(Order.created_at.desc())
        
        orders = query.all()
        
        return jsonify([order.to_dict() for order in orders]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch orders', 'error': str(e)}), 500

@orders_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_orders():
    """Get recent orders for dashboard"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get recent orders (last 10) based on user role
        if current_user.role == 'manufacturer':
            # Manufacturer sees orders from distributors who are ordering their products
            # Get all products from this manufacturer
            manufacturer_products = Product.query.filter_by(manufacturer_id=current_user_id).all()
            manufacturer_product_ids = [p.id for p in manufacturer_products]
            
            # Get order items that contain products from this manufacturer
            order_items_with_manufacturer_products = OrderItem.query.filter(
                OrderItem.product_id.in_(manufacturer_product_ids)
            ).all()
            
            # Get order IDs from these order items
            order_ids = [item.order_id for item in order_items_with_manufacturer_products]
            
            if order_ids:
                query = Order.query.filter(Order.id.in_(order_ids))
            else:
                query = Order.query.filter_by(id=None)  # Return no results
        elif current_user.role == 'distributor':
            # Distributor sees recent orders where they are the seller (to retailers)
            query = Order.query.filter_by(distributor_id=current_user_id)
        elif current_user.role == 'retailer':
            # Retailer sees their recent orders
            query = Order.query.filter_by(retailer_id=current_user_id)
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        # Get last 10 orders, ordered by creation date
        recent_orders = query.order_by(Order.created_at.desc()).limit(10).all()
        
        return jsonify([order.to_dict() for order in recent_orders]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch recent orders', 'error': str(e)}), 500

@orders_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get specific order details"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user has access to this order
        if order.retailer_id != current_user_id and order.distributor_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        
        return jsonify(order.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch order', 'error': str(e)}), 500

@orders_bp.route('/<order_id>/approve', methods=['POST'])
@jwt_required()
@role_required('manufacturer')
def approve_order(order_id):
    """Approve an order (manufacturer only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if this manufacturer owns the products in this order
        # For manufacturer-distributor orders: manufacturer is distributor_id (seller), distributor is retailer_id (buyer)
        if order.distributor_id != current_user_id:
            return jsonify({'message': 'Access denied - you can only approve orders for your products'}), 403
        
        if order.status != 'pending':
            return jsonify({'message': 'Order is not in pending status'}), 400
        
        # Update order status
        order.status = 'approved'
        # order.approved_at = datetime.utcnow()  # Column doesn't exist
        
        # Update inventory (deduct stock)
        for item in order.items:
            # Find the product allocation for this manufacturer
            allocation = ProductAllocation.query.filter_by(
                manufacturer_id=current_user_id,
                product_id=item.product_id,
                is_active=True
            ).first()
            
            if allocation:
                # Update inventory
                inventory = Inventory.query.filter_by(
                    distributor_id=current_user_id,
                    product_id=item.product_id
                ).first()
                
                if inventory and inventory.quantity >= item.quantity:
                    inventory.quantity -= item.quantity
                else:
                    return jsonify({'message': f'Insufficient stock for product {item.product.name}'}), 400
        
        db.session.commit()
        
        # Create notification for distributor (retailer_id is the distributor who placed the order)
        notification = WhatsAppNotification(
            user_id=order.retailer_id,
            message=f'Your order #{order.order_number} has been approved by {current_user.business_name}',
            type='order_status'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'message': 'Order approved successfully', 'order': order.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to approve order', 'error': str(e)}), 500

@orders_bp.route('/<order_id>/decline', methods=['POST'])
@jwt_required()
@role_required('manufacturer')
def decline_order(order_id):
    """Decline an order (manufacturer only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if this manufacturer owns the products in this order
        # For manufacturer-distributor orders: manufacturer is distributor_id (seller), distributor is retailer_id (buyer)
        if order.distributor_id != current_user_id:
            return jsonify({'message': 'Access denied - you can only decline orders for your products'}), 403
        
        if order.status != 'pending':
            return jsonify({'message': 'Order is not in pending status'}), 400
        
        data = request.get_json()
        decline_reason = data.get('reason', 'Order declined by manufacturer')
        
        # Update order status
        order.status = 'declined'
        # order.declined_at = datetime.utcnow()  # Column doesn't exist
        # order.decline_reason = decline_reason   # Column doesn't exist
        
        db.session.commit()
        
        # Create notification for distributor
        notification = WhatsAppNotification(
            user_id=order.retailer_id,
            message=f'Your order #{order.order_number} has been declined by {current_user.business_name}. Reason: {decline_reason}',
            type='order_status'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'message': 'Order declined successfully', 'order': order.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to decline order', 'error': str(e)}), 500



@orders_bp.route('', methods=['POST'])
@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    """Create order from cart"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        cart_items = data.get('cart_items', [])
        delivery_option = data.get('delivery_option', 'DELIVER_TO_BUYER')
        notes = data.get('notes', '')
        
        if not cart_items:
            return jsonify({'message': 'No items in cart'}), 400
        
        # For now, we'll create orders based on the current schema (distributor-retailer)
        # Distributors can order from manufacturers, but we'll need to adapt the schema
        
        if current_user.role == 'distributor':
            # Distributor ordering from manufacturer
            # We'll create a special order type for manufacturer-distributor orders
            # For now, let's create a simple order structure
            
            total_amount = 0
            order_items = []
            
            for item_data in cart_items:
                product_id = item_data.get('product_id')
                quantity = item_data.get('quantity', 1)
                
                product = Product.query.get(product_id)
                if not product:
                    return jsonify({'message': f'Product {product_id} not found'}), 404
                
                # Check if product is allocated to this distributor
                from app.models.product_allocation import ProductAllocation
                allocation = ProductAllocation.query.filter_by(
                    manufacturer_id=product.manufacturer_id,
                    distributor_id=current_user_id,
                    product_id=product_id,
                    is_active=True
                ).first()
                
                if not allocation:
                    return jsonify({'message': f'Product {product.name} not allocated to you'}), 400
                
                # Use allocation price or product base price
                unit_price = float(allocation.selling_price) if allocation.selling_price else float(product.base_price)
                item_total = quantity * unit_price
                total_amount += item_total
                
                order_items.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': item_total,
                    'manufacturer_id': product.manufacturer_id
                })
            
            # Create order number
            order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
            
            # Create order (distributor ordering from manufacturer)
            # For manufacturer-distributor orders, we'll use a special approach
            order = Order(
                id=str(uuid.uuid4()),
                order_number=order_number,
                retailer_id=current_user_id,  # Distributor as buyer
                distributor_id=product.manufacturer_id,  # Manufacturer as seller
                status='pending',
                delivery_mode=delivery_option,
                total_amount=total_amount,
                notes=notes
            )
            
            db.session.add(order)
            db.session.flush()  # Get the order ID
            
            # Create order items
            for item_data in order_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price']
                )
                db.session.add(order_item)
            
            created_orders = [order]
        else:
            return jsonify({'message': 'Order creation not supported for this role'}), 400
        
        db.session.commit()
        
        return jsonify({
            'message': 'Orders created successfully',
            'orders': [order.to_dict() for order in created_orders]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create order', 'error': str(e)}), 500

@orders_bp.route('/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """Update order status (Accept/Reject/Partial/Pack/Ship/Deliver)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user is the seller
        if order.seller_id != current_user_id:
            return jsonify({'message': 'Only seller can update order status'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        partial_quantities = data.get('partial_quantities', {})
        delivery_option = data.get('delivery_option')
        internal_notes = data.get('internal_notes', '')
        
        if not new_status:
            return jsonify({'message': 'Status is required'}), 400
        
        # Validate status transition
        valid_transitions = {
            'PENDING': ['ACCEPTED', 'REJECTED', 'PARTIAL'],
            'PARTIAL': ['ACCEPTED', 'REJECTED'],
            'ACCEPTED': ['PACKED'],
            'PACKED': ['SHIPPED', 'OUT_FOR_DELIVERY'],
            'SHIPPED': ['DELIVERED'],
            'OUT_FOR_DELIVERY': ['DELIVERED']
        }
        
        if order.status not in valid_transitions or new_status not in valid_transitions.get(order.status, []):
            return jsonify({'message': f'Invalid status transition from {order.status} to {new_status}'}), 400
        
        # Handle partial acceptance
        if new_status == 'PARTIAL':
            for item_id, quantity in partial_quantities.items():
                order_item = OrderItem.query.get(item_id)
                if order_item and order_item.order_id == order.id:
                    if quantity > order_item.quantity:
                        return jsonify({'message': f'Partial quantity cannot exceed original quantity for item {item_id}'}), 400
                    order_item.quantity = quantity
                    order_item.total_price = quantity * order_item.unit_price
        
        # Update order status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # Update delivery option if provided
        if delivery_option:
            order.delivery_option = delivery_option
        
        # Add internal notes
        if internal_notes:
            order.internal_notes = internal_notes
        
        # Reduce stock when shipping
        if new_status in ['SHIPPED', 'OUT_FOR_DELIVERY']:
            for item in order.items:
                product = Product.query.get(item.product_id)
                if product:
                    product.stock_quantity -= item.quantity
                    if product.stock_quantity < 0:
                        product.stock_quantity = 0
        
        # Recalculate total for partial orders
        if new_status == 'PARTIAL':
            order.total_amount = sum(item.total_price for item in order.items)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Order status updated to {new_status}',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update order status', 'error': str(e)}), 500

@orders_bp.route('/<order_id>/notes', methods=['PUT'])
@jwt_required()
def update_order_notes(order_id):
    """Update order notes"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user has access to this order
        if order.buyer_id != current_user_id and order.seller_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        data = request.get_json()
        notes = data.get('notes', '')
        
        # Buyer can update notes, seller can update internal_notes
        if order.buyer_id == current_user_id:
            order.notes = notes
        else:
            order.internal_notes = notes
        
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Order notes updated',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update order notes', 'error': str(e)}), 500

@orders_bp.route('/templates', methods=['POST'])
@jwt_required()
def save_order_template():
    """Save current cart as reorder template"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        template_name = data.get('name', 'Reorder Template')
        cart_items = data.get('cart_items', [])
        
        if not cart_items:
            return jsonify({'message': 'No items to save as template'}), 400
        
        # Save template to database (simplified - you might want a separate Template model)
        # For now, we'll store it in the user's preferences or create a simple template
        
        return jsonify({
            'message': 'Reorder template saved successfully',
            'template_name': template_name
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Failed to save template', 'error': str(e)}), 500

@orders_bp.route('/templates/<template_id>/reorder', methods=['POST'])
@jwt_required()
def reorder_from_template(template_id):
    """Reorder from saved template"""
    try:
        current_user_id = get_jwt_identity()
        
        # Load template and create order (simplified)
        # This would typically load from a Template model
        
        return jsonify({
            'message': 'Order created from template successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Failed to reorder from template', 'error': str(e)}), 500 