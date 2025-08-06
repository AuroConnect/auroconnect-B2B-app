from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.product import Product
from models.inventory import Inventory
from models.order import Order, OrderItem, OrderStatusEnum, FulfillmentTypeEnum
from models.invoice import Invoice
from models.notification import Notification, NotificationTypeEnum
from datetime import datetime, timedelta
import os

distributor_bp = Blueprint('distributor', __name__)

# Helper function to check if user is distributor
def check_distributor():
    if not current_user.is_distributor():
        return jsonify({'error': {'code': 'UNAUTHORIZED', 'message': 'Access denied. Distributor role required.'}}), 403
    return None

@distributor_bp.route('/inventory', methods=['GET'])
@login_required
def list_inventory():
    """Get list of assigned inventory"""
    # Check if user is distributor
    error = check_distributor()
    if error:
        return error
    
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '', type=str)
        low_stock = request.args.get('low_stock', '', type=str)
        
        # Build query
        query = Inventory.query.filter_by(distributor_id=current_user.id)
        
        # Join with product for search and filtering
        query = query.join(Product)
        
        # Apply search filter
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Product.name.ilike(search_filter),
                    Product.sku.ilike(search_filter)
                )
            )
        
        # Apply low stock filter
        if low_stock:
            query = query.filter(Inventory.available_quantity <= 10)
        
        # Order by last updated
        query = query.order_by(Inventory.last_updated.desc())
        
        # Paginate results
        inventories = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [inventory.to_dict() for inventory in inventories.items],
            'meta': {
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': inventories.total,
                    'pages': inventories.pages
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'LIST_INVENTORY_ERROR', 'message': 'Failed to list inventory', 'details': str(e)}}), 500

@distributor_bp.route('/orders', methods=['GET'])
@login_required
def list_orders():
    """Get list of incoming orders"""
    # Check if user is distributor
    error = check_distributor()
    if error:
        return error
    
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status', '', type=str)
        search = request.args.get('search', '', type=str)
        
        # Build query
        query = Order.query.filter_by(distributor_id=current_user.id)
        
        # Apply status filter
        if status:
            try:
                status_enum = OrderStatusEnum(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                pass  # Invalid status, ignore filter
        
        # Apply search filter (search in retailer company name)
        if search:
            search_filter = f"%{search}%"
            query = query.join(User, Order.retailer_id == User.id).filter(
                User.company_name.ilike(search_filter)
            )
        
        # Order by creation date
        query = query.order_by(Order.created_at.desc())
        
        # Paginate results
        orders = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get order details with items
        orders_data = []
        for order in orders.items:
            order_data = order.to_dict()
            # Add order items
            order_data['items'] = [item.to_dict() for item in order.order_items]
            orders_data.append(order_data)
        
        return jsonify({
            'data': orders_data,
            'meta': {
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': orders.total,
                    'pages': orders.pages
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'LIST_ORDERS_ERROR', 'message': 'Failed to list orders', 'details': str(e)}}), 500

@distributor_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    """Get details of a specific order"""
    # Check if user is distributor
    error = check_distributor()
    if error:
        return error
    
    try:
        # Get order and ensure it belongs to current distributor
        order = Order.query.filter_by(id=order_id, distributor_id=current_user.id).first()
        if not order:
            return jsonify({'error': {'code': 'ORDER_NOT_FOUND', 'message': 'Order not found'}}), 404
        
        # Get order details with items
        order_data = order.to_dict()
        order_data['items'] = [item.to_dict() for item in order.order_items]
        
        # Add retailer details
        order_data['retailer'] = {
            'id': order.retailer.id,
            'name': order.retailer.name,
            'company_name': order.retailer.company_name,
            'email': order.retailer.email,
            'phone': order.retailer.phone
        }
        
        return jsonify({
            'data': order_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'GET_ORDER_ERROR', 'message': 'Failed to get order', 'details': str(e)}}), 500

@distributor_bp.route('/orders/<int:order_id>/accept', methods=['POST'])
@login_required
def accept_order(order_id):
    """Accept an order"""
    # Check if user is distributor
    error = check_distributor()
    if error:
        return error
    
    try:
        # Get order and ensure it belongs to current distributor
        order = Order.query.filter_by(id=order_id, distributor_id=current_user.id).first()
        if not order:
            return jsonify({'error': {'code': 'ORDER_NOT_FOUND', 'message': 'Order not found'}}), 404
        
        # Check if order is in pending status
        if order.status != OrderStatusEnum.PENDING:
            return jsonify({'error': {'code': 'INVALID_STATUS', 'message': 'Order is not in pending status'}}), 400
        
        # Get fulfillment type from request
        data = request.get_json()
        fulfillment_type = data.get('fulfillment_type') if data else None
        
        # Validate fulfillment type
        if fulfillment_type:
            try:
                fulfillment_enum = FulfillmentTypeEnum(fulfillment_type)
                order.fulfillment_type = fulfillment_enum
            except ValueError:
                return jsonify({'error': {'code': 'INVALID_FULFILLMENT', 'message': 'Invalid fulfillment type'}}), 400
        else:
            # Default to delivery if not specified
            order.fulfillment_type = FulfillmentTypeEnum.DELIVERY
        
        # Update order status
        order.update_status(OrderStatusEnum.ACCEPTED)
        order.updated_at = datetime.utcnow()
        
        # Reserve inventory for order items
        for item in order.order_items:
            inventory = Inventory.query.filter_by(
                product_id=item.product_id,
                distributor_id=current_user.id
            ).first()
            
            if inventory:
                if not inventory.reserve_quantity(item.quantity):
                    # Not enough inventory, rollback
                    db.session.rollback()
                    return jsonify({'error': {'code': 'INSUFFICIENT_INVENTORY', 'message': f'Insufficient inventory for {item.product.name}'}}), 400
        
        # Create notification for retailer
        notification = Notification(
            user_id=order.retailer_id,
            order_id=order.id,
            message=f"✅ Your order #{order.id} has been accepted by {current_user.company_name}.",
            type=NotificationTypeEnum.ORDER
        )
        db.session.add(notification)
        
        # Commit changes
        db.session.commit()
        
        # Get updated order details
        order_data = order.to_dict()
        order_data['items'] = [item.to_dict() for item in order.order_items]
        
        return jsonify({
            'data': {
                'message': 'Order accepted successfully',
                'order': order_data
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': {'code': 'ACCEPT_ORDER_ERROR', 'message': 'Failed to accept order', 'details': str(e)}}), 500

@distributor_bp.route('/orders/<int:order_id>/reject', methods=['POST'])
@login_required
def reject_order(order_id):
    """Reject an order"""
    # Check if user is distributor
    error = check_distributor()
    if error:
        return error
    
    try:
        # Get order and ensure it belongs to current distributor
        order = Order.query.filter_by(id=order_id, distributor_id=current_user.id).first()
        if not order:
            return jsonify({'error': {'code': 'ORDER_NOT_FOUND', 'message': 'Order not found'}}), 404
        
        # Check if order is in pending status
        if order.status != OrderStatusEnum.PENDING:
            return jsonify({'error': {'code': 'INVALID_STATUS', 'message': 'Order is not in pending status'}}), 400
        
        # Get rejection reason from request
        data = request.get_json()
        reason = data.get('reason', 'No reason provided') if data else 'No reason provided'
        
        # Update order status
        order.update_status(OrderStatusEnum.REJECTED)
        order.updated_at = datetime.utcnow()
        
        # Create notification for retailer
        notification = Notification(
            user_id=order.retailer_id,
            order_id=order.id,
            message=f"❌ Your order #{order.id} has been rejected by {current_user.company_name}. Reason: {reason}",
            type=NotificationTypeEnum.ORDER
        )
        db.session.add(notification)
        
        # Commit changes
        db.session.commit()
        
        return jsonify({
            'data': {
                'message': 'Order rejected successfully',
                'order': order.to_dict()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': {'code': 'REJECT_ORDER_ERROR', 'message': 'Failed to reject order', 'details': str(e)}}), 500

@distributor_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    """Update order status"""
    # Check if user is distributor
    error = check_distributor()
    if error:
        return error
    
    try:
        # Get order and ensure it belongs to current distributor
        order = Order.query.filter_by(id=order_id, distributor_id=current_user.id).first()
        if not order:
            return jsonify({'error': {'code': 'ORDER_NOT_FOUND', 'message': 'Order not found'}}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if 'status' not in data:
            return jsonify({'error': {'code': 'MISSING_FIELD', 'message': 'status is required'}}), 400
        
        # Validate status
        try:
            new_status = OrderStatusEnum(data['status'])
        except ValueError:
            return jsonify({'error': {'code': 'INVALID_STATUS', 'message': 'Invalid status'}}), 400
        
        # Check if status transition is valid
        if not order.can_update_status(new_status):
            return jsonify({'error': {'code': 'INVALID_TRANSITION', 'message': 'Invalid status transition'}}), 400
        
        # Update status
        old_status = order.status
        order.update_status(new_status)
        order.updated_at = datetime.utcnow()
        
        # If status is delivered, generate invoice and deduct inventory
        if new_status == OrderStatusEnum.DELIVERED:
            # Deduct reserved inventory
            for item in order.order_items:
                inventory = Inventory.query.filter_by(
                    product_id=item.product_id,
                    distributor_id=current_user.id
                ).first()
                
                if inventory:
                    inventory.deduct_reserved_quantity(item.quantity)
            
            # Generate invoice if not already exists
            if not order.invoice:
                subtotal = order.get_total_amount()
                tax_rate = 18.0  # 18% tax
                tax_amount = subtotal * (tax_rate / 100)
                total = subtotal + tax_amount
                
                invoice = Invoice(
                    order_id=order.id,
                    subtotal=subtotal,
                    tax_rate=tax_rate,
                    tax_amount=tax_amount,
                    total=total,
                    issued_at=datetime.utcnow(),
                    due_date=datetime.utcnow() + timedelta(days=30)  # 30 days payment term
                )
                db.session.add(invoice)
                db.session.flush()  # Get invoice ID
                
                # Generate invoice number
                invoice.invoice_number = invoice.generate_invoice_number()
        
        # Create notification for retailer
        status_display = order.get_status_display()
        notification = Notification(
            user_id=order.retailer_id,
            order_id=order.id,
            message=f"📦 Order #{order.id} status updated to {status_display}.",
            type=NotificationTypeEnum.ORDER
        )
        db.session.add(notification)
        
        # Commit changes
        db.session.commit()
        
        # Get updated order details
        order_data = order.to_dict()
        order_data['items'] = [item.to_dict() for item in order.order_items]
        
        return jsonify({
            'data': {
                'message': 'Order status updated successfully',
                'order': order_data
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': {'code': 'UPDATE_STATUS_ERROR', 'message': 'Failed to update order status', 'details': str(e)}}), 500

@distributor_bp.route('/invoices', methods=['GET'])
@login_required
def list_invoices():
    """Get list of invoices"""
    # Check if user is distributor
    error = check_distributor()
    if error:
        return error
    
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '', type=str)
        
        # Build query
        query = db.session.query(Invoice).join(Order).filter(
            Order.distributor_id == current_user.id
        )
        
        # Apply search filter (search in invoice number)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(Invoice.invoice_number.ilike(search_filter))
        
        # Order by issue date
        query = query.order_by(Invoice.issued_at.desc())
        
        # Paginate results
        invoices = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'data': [invoice.to_dict() for invoice in invoices.items],
            'meta': {
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': invoices.total,
                    'pages': invoices.pages
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'LIST_INVOICES_ERROR', 'message': 'Failed to list invoices', 'details': str(e)}}), 500

@distributor_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
@login_required
def get_invoice(invoice_id):
    """Get details of a specific invoice"""
    # Check if user is distributor
    error = check_distributor()
    if error:
        return error
    
    try:
        # Get invoice and ensure it belongs to current distributor's order
        invoice = db.session.query(Invoice).join(Order).filter(
            Invoice.id == invoice_id,
            Order.distributor_id == current_user.id
        ).first()
        
        if not invoice:
            return jsonify({'error': {'code': 'INVOICE_NOT_FOUND', 'message': 'Invoice not found'}}), 404
        
        # Get invoice details
        invoice_data = invoice.to_dict()
        
        # Add order details
        order = invoice.order
        invoice_data['order'] = {
            'id': order.id,
            'retailer': {
                'id': order.retailer.id,
                'name': order.retailer.name,
                'company_name': order.retailer.company_name
            },
            'items': [item.to_dict() for item in order.order_items],
            'total_amount': float(order.get_total_amount())
        }
        
        return jsonify({
            'data': invoice_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'GET_INVOICE_ERROR', 'message': 'Failed to get invoice', 'details': str(e)}}), 500