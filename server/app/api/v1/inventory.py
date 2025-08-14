from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.utils.decorators import roles_required
from app import db
from sqlalchemy import and_, or_
import openpyxl
from io import BytesIO
from datetime import datetime
import uuid

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/', methods=['GET'])
@jwt_required()
def get_inventory():
    """Get inventory items for current user"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Get inventory based on user role
    if user.role == 'manufacturer':
        # Manufacturers see their products' inventory across distributors
        inventory_items = db.session.query(Inventory).join(Product).filter(
            Product.manufacturer_id == current_user_id
        ).all()
    elif user.role == 'distributor':
        # Distributors see their own inventory
        inventory_items = Inventory.query.filter_by(distributor_id=current_user_id).all()
    else:
        # Retailers don't manage inventory directly
        return jsonify({'message': 'Access denied'}), 403
    
    return jsonify({
        'inventory': [item.to_dict() for item in inventory_items],
        'summary': {
            'totalItems': len(inventory_items),
            'lowStockItems': len([item for item in inventory_items if item.is_low_stock]),
            'outOfStockItems': len([item for item in inventory_items if item.available_quantity == 0])
        }
    })

@inventory_bp.route('/<inventory_id>', methods=['GET'])
@jwt_required()
def get_inventory_item(inventory_id):
    """Get specific inventory item"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    inventory_item = Inventory.query.get(inventory_id)
    if not inventory_item:
        return jsonify({'message': 'Inventory item not found'}), 404
    
    # Check access permissions
    if user.role == 'manufacturer':
        product = Product.query.get(inventory_item.product_id)
        if not product or product.manufacturer_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
    elif user.role == 'distributor':
        if inventory_item.distributor_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
    else:
        return jsonify({'message': 'Access denied'}), 403
    
    return jsonify(inventory_item.to_dict())

@inventory_bp.route('/<inventory_id>', methods=['PUT'])
@jwt_required()
@roles_required(['distributor'])
def update_inventory_item(inventory_id):
    """Update inventory item (distributors only)"""
    current_user_id = get_jwt_identity()
    
    inventory_item = Inventory.query.get(inventory_id)
    if not inventory_item:
        return jsonify({'message': 'Inventory item not found'}), 404
    
    if inventory_item.distributor_id != current_user_id:
        return jsonify({'message': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'quantity' in data:
        inventory_item.quantity = int(data['quantity'])
    if 'lowStockThreshold' in data:
        inventory_item.low_stock_threshold = int(data['lowStockThreshold'])
    if 'autoRestockQuantity' in data:
        inventory_item.auto_restock_quantity = int(data['autoRestockQuantity'])
    if 'sellingPrice' in data:
        inventory_item.selling_price = float(data['sellingPrice'])
    if 'isAvailable' in data:
        inventory_item.is_available = bool(data['isAvailable'])
    
    inventory_item.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Inventory updated successfully',
            'inventory': inventory_item.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update inventory', 'error': str(e)}), 500

@inventory_bp.route('/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock_items():
    """Get low stock items"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Get low stock items based on user role
    if user.role == 'manufacturer':
        low_stock_items = db.session.query(Inventory).join(Product).filter(
            and_(
                Product.manufacturer_id == current_user_id,
                Inventory.available_quantity <= Inventory.low_stock_threshold
            )
        ).all()
    elif user.role == 'distributor':
        low_stock_items = Inventory.query.filter(
            and_(
                Inventory.distributor_id == current_user_id,
                Inventory.available_quantity <= Inventory.low_stock_threshold
            )
        ).all()
    else:
        return jsonify({'message': 'Access denied'}), 403
    
    return jsonify({
        'lowStockItems': [item.to_dict() for item in low_stock_items],
        'count': len(low_stock_items)
    })

@inventory_bp.route('/auto-restock', methods=['POST'])
@jwt_required()
@roles_required(['distributor'])
def auto_restock():
    """Perform auto-restock for low stock items"""
    current_user_id = get_jwt_identity()
    
    # Get all low stock items for this distributor
    low_stock_items = Inventory.query.filter(
        and_(
            Inventory.distributor_id == current_user_id,
            Inventory.needs_restock == True
        )
    ).all()
    
    restocked_items = []
    for item in low_stock_items:
        if item.auto_restock():
            restocked_items.append(item)
    
    try:
        db.session.commit()
        return jsonify({
            'message': f'Auto-restocked {len(restocked_items)} items',
            'restockedItems': [item.to_dict() for item in restocked_items]
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to auto-restock', 'error': str(e)}), 500

@inventory_bp.route('/bulk-update', methods=['POST'])
@jwt_required()
@roles_required(['distributor'])
def bulk_update_inventory():
    """Bulk update inventory via Excel file"""
    current_user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'message': 'Invalid file format. Please upload Excel file'}), 400
    
    try:
        # Read Excel file
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active
        
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        # Skip header row
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row[0]:  # Skip empty rows
                continue
                
            try:
                product_sku = str(row[0]).strip()
                quantity = int(row[1]) if row[1] else 0
                low_stock_threshold = int(row[2]) if row[2] else 10
                auto_restock_quantity = int(row[3]) if row[3] else 50
                selling_price = float(row[4]) if row[4] else None
                
                # Find product by SKU
                product = Product.query.filter_by(sku=product_sku).first()
                if not product:
                    results['errors'].append(f'Product with SKU {product_sku} not found')
                    results['failed'] += 1
                    continue
                
                # Find or create inventory item
                inventory_item = Inventory.query.filter_by(
                    distributor_id=current_user_id,
                    product_id=product.id
                ).first()
                
                if not inventory_item:
                    inventory_item = Inventory(
                        distributor_id=current_user_id,
                        product_id=product.id,
                        quantity=quantity,
                        low_stock_threshold=low_stock_threshold,
                        auto_restock_quantity=auto_restock_quantity,
                        selling_price=selling_price
                    )
                    db.session.add(inventory_item)
                else:
                    inventory_item.quantity = quantity
                    inventory_item.low_stock_threshold = low_stock_threshold
                    inventory_item.auto_restock_quantity = auto_restock_quantity
                    if selling_price:
                        inventory_item.selling_price = selling_price
                    inventory_item.updated_at = datetime.utcnow()
                
                results['success'] += 1
                
            except Exception as e:
                results['errors'].append(f'Row error: {str(e)}')
                results['failed'] += 1
        
        db.session.commit()
        return jsonify({
            'message': 'Bulk update completed',
            'results': results
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to process file', 'error': str(e)}), 500

@inventory_bp.route('/reserve-stock', methods=['POST'])
@jwt_required()
def reserve_stock():
    """Reserve stock for pending orders"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    product_id = data.get('productId')
    quantity = int(data.get('quantity', 0))
    distributor_id = data.get('distributorId')
    
    if not product_id or not quantity or not distributor_id:
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Find inventory item
    inventory_item = Inventory.query.filter_by(
        distributor_id=distributor_id,
        product_id=product_id
    ).first()
    
    if not inventory_item:
        return jsonify({'message': 'Inventory item not found'}), 404
    
    if inventory_item.reserve_stock(quantity):
        try:
            db.session.commit()
            return jsonify({
                'message': 'Stock reserved successfully',
                'inventory': inventory_item.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Failed to reserve stock', 'error': str(e)}), 500
    else:
        return jsonify({'message': 'Insufficient available stock'}), 400

@inventory_bp.route('/release-stock', methods=['POST'])
@jwt_required()
def release_stock():
    """Release reserved stock"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    product_id = data.get('productId')
    quantity = int(data.get('quantity', 0))
    distributor_id = data.get('distributorId')
    
    if not product_id or not quantity or not distributor_id:
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Find inventory item
    inventory_item = Inventory.query.filter_by(
        distributor_id=distributor_id,
        product_id=product_id
    ).first()
    
    if not inventory_item:
        return jsonify({'message': 'Inventory item not found'}), 404
    
    inventory_item.release_reserved_stock(quantity)
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Stock released successfully',
            'inventory': inventory_item.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to release stock', 'error': str(e)}), 500

@inventory_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_inventory_analytics():
    """Get inventory analytics"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Get inventory based on user role
    if user.role == 'manufacturer':
        inventory_items = db.session.query(Inventory).join(Product).filter(
            Product.manufacturer_id == current_user_id
        ).all()
    elif user.role == 'distributor':
        inventory_items = Inventory.query.filter_by(distributor_id=current_user_id).all()
    else:
        return jsonify({'message': 'Access denied'}), 403
    
    # Calculate analytics
    total_quantity = sum(item.quantity for item in inventory_items)
    total_reserved = sum(item.reserved_quantity for item in inventory_items)
    total_available = sum(item.available_quantity for item in inventory_items)
    low_stock_count = len([item for item in inventory_items if item.is_low_stock])
    out_of_stock_count = len([item for item in inventory_items if item.available_quantity == 0])
    
    # Calculate total value
    total_value = sum(
        item.quantity * (item.selling_price or 0) 
        for item in inventory_items 
        if item.selling_price
    )
    
    return jsonify({
        'analytics': {
            'totalItems': len(inventory_items),
            'totalQuantity': total_quantity,
            'totalReserved': total_reserved,
            'totalAvailable': total_available,
            'lowStockCount': low_stock_count,
            'outOfStockCount': out_of_stock_count,
            'totalValue': float(total_value),
            'averageStockLevel': total_quantity / len(inventory_items) if inventory_items else 0
        }
    })
