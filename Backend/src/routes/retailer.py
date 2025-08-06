from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.product import Product
from models.inventory import Inventory
from models.order import Order, OrderItem, OrderStatusEnum
from models.invoice import Invoice
from models.notification import Notification, NotificationTypeEnum
from datetime import datetime
import os

retailer_bp = Blueprint('retailer', __name__)

# Helper function to check if user is retailer
def check_retailer():
    if not current_user.is_retailer():
        return jsonify({'error': {'code': 'UNAUTHORIZED', 'message': 'Access denied. Retailer role required.'}}), 403
    return None

@retailer_bp.route('/catalog', methods=['GET'])
@login_required
def browse_catalog():
    """Browse product catalog from assigned distributor"""
    # Check if user is retailer
    error = check_retailer()
    if error:
        return error
    
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '', type=str)
        category = request.args.get('category', '', type=str)
        distributor_id = request.args.get('distributor_id', type=int)
        
        # Build query for products with available inventory
        query = db.session.query(Product).join(Inventory).filter(
            Inventory.quantity > 0,
            Inventory.distributor_id == (distributor_id if distributor_id else current_user.id)
        )
        
        # Apply search filter
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Product.name.ilike(search_filter),
                    Product.description.ilike(search_filter),
                    Product.sku.ilike(search_filter)
                )
            )
        
        # Apply category filter
        if category:
            query = query.filter(Product.category == category)
        
        # Order by product name
        query = query.order_by(Product.name.asc())
        
        # Paginate results
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Add inventory information to products
        products_data = []
        for product in products.items:
            product_data = product.to_dict()
            
            # Get inventory info for this product
            inventory = Inventory.query.filter_by(
                product_id=product.id,
                distributor_id=(distributor_id if distributor_id else current_user.id)
            ).first()
            
            if inventory:
                product_data['inventory'] = {
                    'available_quantity': inventory.available_quantity,
                    'reserved_quantity': inventory.reserved_quantity
                }
            
            products_data.append(product_data)
        
        return jsonify({
            'data': products_data,
            'meta': {
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': products.total,
                    'pages': products.pages
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'BROWSE_CATALOG_ERROR', 'message': 'Failed to browse catalog', 'details': str(e)}}), 500

@retailer_bp.route('/catalog/<int:product_id>', methods=['GET'])
@login_required
def get_product_details(product_id):
    """Get details of a specific product"""
    # Check if user is retailer
    error = check_retailer()
    if error:
        return error
    
    try:
        # Get product with inventory information
        product = db.session.query(Product).join(Inventory).filter(
            Product.id == product_id,
            Inventory.quantity > 0
        ).first()
        
        if not product:
            return jsonify({'error': {'code': 'PRODUCT_NOT_FOUND', 'message': 'Product not found or out of stock'}}), 404
        
        # Get product details
        product_data = product.to_dict()
        
        # Add inventory information
        inventory = Inventory.query.filter_by(product_id=product.id).first()
        if inventory:
            product_data['inventory'] = {
                'available_quantity': inventory.available_quantity,
                'reserved_quantity': inventory.reserved_quantity
            }
        
        return jsonify({
            'data': product_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'GET_PRODUCT_ERROR', 'message': 'Failed to get product', 'details': str(e)}}), 500

@retailer_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    """Create a new order"""
    # Check if user is retailer
    error = check_retailer()
    if error:
        return error
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'distributor_id' not in data:
            return jsonify({'error': {'code': 'MISSING_FIELD', 'message': 'distributor_id is required'}}), 400
        
        if 'items' not in data or not data['items']:
            return jsonify({'error': {'code': 'MISSING_FIELD', 'message': 'items is required'}}), 400
        
        # Check if distributor exists and is actually a distributor
        distributor = User.query.filter_by(id=data['distributor_id']).first()
        if not distributor or not distributor.is_distributor():
            return jsonify({'error': {'code': 'INVALID_DISTRIBUTOR', 'message': 'Invalid distributor'}}), 400
        
        # Validate order items
        items_data = data['items']
        if not isinstance(items_data, list) or len(items_data) == 0:
            return jsonify({'error': {'code': 'INVALID_ITEMS', 'message': 'Items must be a non-empty array'}}), 400
        
        # Calculate total amount and validate inventory
        total_amount = 0
        order_items = []
        
        for item_data in items_data:
            # Validate item fields
            if 'product_id' not in item_data or 'quantity' not in item_data:
                return jsonify({'error': {'code': 'MISSING_FIELD', 'message': 'Each item must have product_id and quantity'}}), 400
            
            # Validate quantity
            try:
                quantity = int(item_data['quantity'])
                if quantity <= 0:
                    return jsonify({'error': {'code': 'INVALID_QUANTITY', 'message': 'Quantity must be positive'}}), 400
            except (ValueError, TypeError):
                return jsonify({'error': {'code': 'INVALID_QUANTITY', 'message': 'Invalid quantity format'}}), 400
            
            # Get product and check inventory
            product = Product.query.filter_by(id=item_data['product_id']).first()
            if not product:
                return jsonify({'error': {'code': 'PRODUCT_NOT_FOUND', 'message': f'Product {item_data["product_id"]} not found'}}), 404
            
            inventory = Inventory.query.filter_by(
                product_id=item_data['product_id'],
                distributor_id=data['distributor_id']
            ).first()
            
            if not inventory or inventory.available_quantity < quantity:
                return jsonify({'error': {'code': 'INSUFFICIENT_INVENTORY', 'message': f'Insufficient inventory for {product.name}'}}), 400
            
            # Calculate item total
            item_total = product.price * quantity
            total_amount += item_total
            
            # Create order item
            order_item = OrderItem(
                product_id=item_data['product_id'],
                quantity=quantity,
                unit_price=product.price,
                total_price=item_total
            )
            order_items.append(order_item)
        
        # Create order
        order = Order(
            retailer_id=current_user.id,
            distributor_id=data['distributor_id'],
            status=OrderStatusEnum.PENDING
        )
        
        # Add order items
        for item in order_items:
            order.order_items.append(item)
        
        # Add to database
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create notification for distributor
        notification = Notification(
            user_id=data['distributor_id'],
            order_id=order.id,
            message=f"🛒 New order #{order.id} from {current_user.company_name}. Please acknowledge.",
            type=NotificationTypeEnum.ORDER
        )
        db.session.add(notification)
        
        # Commit changes
        db.session.commit()
        
        # Get order details
        order_data = order.to_dict()
        order_data['items'] = [item.to_dict() for item in order.order_items]
        
        return jsonify({
            'data': {
                'message': 'Order created successfully',
                'order': order_data
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': {'code': 'CREATE_ORDER_ERROR', 'message': 'Failed to create order', 'details': str(e)}}), 500

@retailer_bp.route('/orders', methods=['GET'])
@login_required
def list_orders():
    """Get list of orders"""
    # Check if user is retailer
    error = check_retailer()
    if error:
        return error
    
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status', '', type=str)
        search = request.args.get('search', '', type=str)
        
        # Build query
        query = Order.query.filter_by(retailer_id=current_user.id)
        
        # Apply status filter
        if status:
            try:
                status_enum = OrderStatusEnum(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                pass  # Invalid status, ignore filter
        
        # Apply search filter (search in distributor company name)
        if search:
            search_filter = f"%{search}%"
            query = query.join(User, Order.distributor_id == User.id).filter(
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

@retailer_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    """Get details of a specific order"""
    # Check if user is retailer
    error = check_retailer()
    if error:
        return error
    
    try:
        # Get order and ensure it belongs to current retailer
        order = Order.query.filter_by(id=order_id, retailer_id=current_user.id).first()
        if not order:
            return jsonify({'error': {'code': 'ORDER_NOT_FOUND', 'message': 'Order not found'}}), 404
        
        # Get order details with items
        order_data = order.to_dict()
        order_data['items'] = [item.to_dict() for item in order.order_items]
        
        # Add distributor details
        order_data['distributor'] = {
            'id': order.distributor_orders.id,
            'name': order.distributor_orders.name,
            'company_name': order.distributor_orders.company_name,
            'email': order.distributor_orders.email,
            'phone': order.distributor_orders.phone
        }
        
        return jsonify({
            'data': order_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'GET_ORDER_ERROR', 'message': 'Failed to get order', 'details': str(e)}}), 500

@retailer_bp.route('/invoices', methods=['GET'])
@login_required
def list_invoices():
    """Get list of invoices"""
    # Check if user is retailer
    error = check_retailer()
    if error:
        return error
    
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '', type=str)
        
        # Build query
        query = db.session.query(Invoice).join(Order).filter(
            Order.retailer_id == current_user.id
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

@retailer_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
@login_required
def get_invoice(invoice_id):
    """Get details of a specific invoice"""
    # Check if user is retailer
    error = check_retailer()
    if error:
        return error
    
    try:
        # Get invoice and ensure it belongs to current retailer's order
        invoice = db.session.query(Invoice).join(Order).filter(
            Invoice.id == invoice_id,
            Order.retailer_id == current_user.id
        ).first()
        
        if not invoice:
            return jsonify({'error': {'code': 'INVOICE_NOT_FOUND', 'message': 'Invoice not found'}}), 404
        
        # Get invoice details
        invoice_data = invoice.to_dict()
        
        # Add order details
        order = invoice.order
        invoice_data['order'] = {
            'id': order.id,
            'distributor': {
                'id': order.distributor_orders.id,
                'name': order.distributor_orders.name,
                'company_name': order.distributor_orders.company_name
            },
            'items': [item.to_dict() for item in order.order_items],
            'total_amount': float(order.get_total_amount())
        }
        
        return jsonify({
            'data': invoice_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': {'code': 'GET_INVOICE_ERROR', 'message': 'Failed to get invoice', 'details': str(e)}}), 500