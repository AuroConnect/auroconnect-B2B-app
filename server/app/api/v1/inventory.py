import pandas as pd
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Inventory, Product, User
from app.utils.decorators import role_required

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/', methods=['GET'])
@jwt_required()
@role_required('distributor')
def get_inventory():
    """Get inventory for current distributor"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get inventory items for the distributor
        inventory_items = db.session.query(Inventory).filter_by(
            distributor_id=current_user_id
        ).all()
        
        # Get analytics
        total_items = len(inventory_items)
        total_quantity = sum(item.quantity for item in inventory_items)
        low_stock_count = len([item for item in inventory_items if item.quantity <= item.low_stock_threshold])
        total_value = sum(item.quantity * item.selling_price for item in inventory_items if item.selling_price)
        
        analytics = {
            'totalItems': total_items,
            'totalQuantity': total_quantity,
            'lowStockCount': low_stock_count,
            'totalValue': total_value
        }
        
        # Format inventory items
        formatted_items = []
        for item in inventory_items:
            product = Product.query.get(item.product_id)
            if product:
                formatted_items.append({
                    'id': str(item.id),
                    'productId': str(item.product_id),
                    'productName': product.name,
                    'sku': product.sku,
                    'quantity': item.quantity,
                    'reservedQuantity': item.reserved_quantity or 0,
                    'availableQuantity': item.quantity - (item.reserved_quantity or 0),
                    'lowStockThreshold': item.low_stock_threshold or 10,
                    'autoRestockQuantity': item.auto_restock_quantity or 50,
                    'isLowStock': item.quantity <= (item.low_stock_threshold or 10),
                    'needsRestock': item.quantity <= (item.low_stock_threshold or 10),
                    'sellingPrice': float(item.selling_price) if item.selling_price else 0,
                    'isAvailable': item.is_available,
                    'lastRestockDate': item.last_restock_date.isoformat() if item.last_restock_date else None,
                    'createdAt': item.created_at.isoformat() if item.created_at else None,
                    'updatedAt': item.updated_at.isoformat() if item.updated_at else None
                })
        
        return jsonify({
            'inventory': formatted_items,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to fetch inventory: {str(e)}'}), 500

@inventory_bp.route('/bulk-upload', methods=['POST'])
@jwt_required()
@role_required('distributor')
def bulk_upload_inventory():
    """Bulk upload inventory from CSV/Excel file"""
    try:
        current_user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        # Check file extension
        allowed_extensions = {'.csv', '.xlsx', '.xls'}
        file_ext = '.' + file.filename.rsplit('.', 1)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'message': 'Invalid file type. Please upload CSV or Excel file.'}), 400
        
        # Read file based on extension
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return jsonify({'message': f'Error reading file: {str(e)}'}), 400
        
        # Validate required columns
        required_columns = ['productId', 'quantity', 'sellingPrice']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'message': f'Missing required columns: {", ".join(missing_columns)}'}), 400
        
        results = []
        
        for index, row in df.iterrows():
            try:
                # Validate required fields
                if pd.isna(row['productId']) or pd.isna(row['quantity']) or pd.isna(row['sellingPrice']):
                    results.append({
                        'row': index + 1,
                        'productName': 'N/A',
                        'status': 'error',
                        'error': 'Missing required fields (productId, quantity, sellingPrice)'
                    })
                    continue
                
                # Check if product exists
                product = Product.query.get(str(row['productId']))
                if not product:
                    results.append({
                        'row': index + 1,
                        'productName': 'N/A',
                        'status': 'error',
                        'error': f'Product with ID {row["productId"]} not found'
                    })
                    continue
                
                # Check if inventory item already exists
                existing_inventory = Inventory.query.filter_by(
                    distributor_id=current_user_id,
                    product_id=str(row['productId'])
                ).first()
                
                if existing_inventory:
                    # Update existing inventory
                    existing_inventory.quantity = int(row['quantity'])
                    existing_inventory.selling_price = float(row['sellingPrice'])
                    if 'lowStockThreshold' in df.columns and not pd.isna(row['lowStockThreshold']):
                        existing_inventory.low_stock_threshold = int(row['lowStockThreshold'])
                    if 'autoRestockQuantity' in df.columns and not pd.isna(row['autoRestockQuantity']):
                        existing_inventory.auto_restock_quantity = int(row['autoRestockQuantity'])
                    existing_inventory.updated_at = datetime.utcnow()
                else:
                    # Create new inventory item
                    new_inventory = Inventory(
                        id=str(uuid.uuid4()),
                        distributor_id=current_user_id,
                        product_id=str(row['productId']),
                        quantity=int(row['quantity']),
                        selling_price=float(row['sellingPrice']),
                        low_stock_threshold=int(row.get('lowStockThreshold', 10)),
                        auto_restock_quantity=int(row.get('autoRestockQuantity', 50)),
                        is_available=True
                    )
                    db.session.add(new_inventory)
                
                results.append({
                    'row': index + 1,
                    'productName': product.name,
                    'status': 'success',
                    'productId': str(row['productId'])
                })
                
            except Exception as e:
                results.append({
                    'row': index + 1,
                    'productName': 'N/A',
                    'status': 'error',
                    'error': str(e)
                })
        
        # Commit all successful updates
        db.session.commit()
        
        return jsonify({
            'message': 'Bulk upload completed',
            'results': results,
            'total': len(results),
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'error'])
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Bulk upload failed: {str(e)}'}), 500

@inventory_bp.route('/<inventory_id>/update', methods=['PATCH'])
@jwt_required()
@role_required('distributor')
def update_inventory_item(inventory_id):
    """Update a specific inventory item"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        inventory_item = Inventory.query.filter_by(
            id=inventory_id,
            distributor_id=current_user_id
        ).first()
        
        if not inventory_item:
            return jsonify({'message': 'Inventory item not found'}), 404
        
        # Update fields
        if 'quantity' in data:
            inventory_item.quantity = int(data['quantity'])
        if 'sellingPrice' in data:
            inventory_item.selling_price = float(data['sellingPrice'])
        if 'lowStockThreshold' in data:
            inventory_item.low_stock_threshold = int(data['lowStockThreshold'])
        if 'autoRestockQuantity' in data:
            inventory_item.auto_restock_quantity = int(data['autoRestockQuantity'])
        if 'isAvailable' in data:
            inventory_item.is_available = bool(data['isAvailable'])
        
        inventory_item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Inventory updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update inventory: {str(e)}'}), 500
