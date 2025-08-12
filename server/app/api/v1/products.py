from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.models.inventory import Inventory
from app.utils.decorators import role_required, roles_required
from sqlalchemy import or_
import openpyxl
from werkzeug.utils import secure_filename
import os

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        category_id = request.args.get('categoryId')
        
        query = Product.query.filter_by(is_active=True)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        products = query.all()
        return jsonify([prod.to_dict() for prod in products]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch products', 'error': str(e)}), 500

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch product', 'error': str(e)}), 500

@products_bp.route('/', methods=['POST'])
@jwt_required()
@roles_required(['manufacturer', 'distributor'])
def create_product():
    """Create new product (manufacturers and distributors)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'sku']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Check if SKU already exists
        existing_product = Product.query.filter_by(sku=data['sku']).first()
        if existing_product:
            return jsonify({'message': 'Product with this SKU already exists'}), 409
        
        new_product = Product(
            name=data['name'],
            description=data.get('description'),
            sku=data['sku'],
            category_id=data.get('categoryId'),
            manufacturer_id=current_user_id,
            image_url=data.get('imageUrl'),
            base_price=data.get('basePrice'),
            is_active=True
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify(new_product.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create product', 'error': str(e)}), 500

@products_bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
@roles_required(['manufacturer', 'distributor'])
def update_product(product_id):
    """Update product (manufacturers and distributors)"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Check if user owns this product
        if product.manufacturer_id != current_user_id:
            return jsonify({'message': 'Access denied - you can only edit your own products'}), 403
        
        # Update fields if provided
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'sku' in data:
            # Check if new SKU already exists (excluding current product)
            existing_product = Product.query.filter(
                Product.sku == data['sku'],
                Product.id != product_id
            ).first()
            if existing_product:
                return jsonify({'message': 'Product with this SKU already exists'}), 409
            product.sku = data['sku']
        if 'categoryId' in data:
            product.category_id = data['categoryId']
        if 'basePrice' in data:
            product.base_price = data['basePrice']
        if 'imageUrl' in data:
            product.image_url = data['imageUrl']
        if 'isActive' in data:
            product.is_active = data['isActive']
        
        db.session.commit()
        
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update product', 'error': str(e)}), 500

@products_bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
@role_required(['manufacturer', 'distributor'])
def delete_product(product_id):
    """Delete product (manufacturers and distributors)"""
    try:
        current_user_id = get_jwt_identity()
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Check if user owns this product
        if product.manufacturer_id != current_user_id:
            return jsonify({'message': 'Access denied - you can only delete your own products'}), 403
        
        # Soft delete by setting is_active to False
        product.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete product', 'error': str(e)}), 500

@products_bp.route('/partner/<partner_id>', methods=['GET'])
@jwt_required()
def get_partner_products(partner_id):
    """Get products from a specific partner"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        partner = User.query.get(partner_id)
        
        if not partner:
            return jsonify({'message': 'Partner not found'}), 404
        
        # Check if user can view partner's products
        can_view = False
        if current_user.role == 'retailer' and partner.role == 'distributor':
            can_view = True
        elif current_user.role == 'retailer' and partner.role == 'retailer':
            can_view = True  # Retailers can view other retailers' products
        elif current_user.role == 'distributor' and partner.role == 'manufacturer':
            can_view = True
        elif current_user.role == 'distributor' and partner.role == 'retailer':
            can_view = True  # Distributors can view retailers' products
        elif current_user.role == 'manufacturer' and partner.role == 'distributor':
            can_view = True  # Manufacturers can view distributors' products
        
        if not can_view:
            return jsonify({'message': 'Access denied'}), 403
        
        # Get products from partner based on their role
        if partner.role == 'distributor':
            # For distributors, get products from their inventory
            inventory_items = Inventory.query.filter_by(
                distributor_id=partner_id,
                is_available=True
            ).all()
            
            products = []
            for item in inventory_items:
                product = Product.query.get(item.product_id)
                if product and product.is_active:
                    product_dict = product.to_dict()
                    # Add inventory information
                    product_dict['inventoryId'] = str(item.id)
                    product_dict['quantity'] = item.quantity
                    product_dict['sellingPrice'] = float(item.selling_price) if item.selling_price else None
                    products.append(product_dict)
        elif partner.role == 'retailer':
            # Retailers don't have products to sell - they only buy
            products = []
        else:
            # For manufacturers, get products directly
            products = Product.query.filter_by(
                manufacturer_id=partner_id,
                is_active=True
            ).all()
            products = [prod.to_dict() for prod in products]
        
        return jsonify(products), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch partner products', 'error': str(e)}), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.all()
        return jsonify([cat.to_dict() for cat in categories]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch categories', 'error': str(e)}), 500

@products_bp.route('/search', methods=['GET'])
def search_products():
    """Search products"""
    try:
        search_term = request.args.get('q', '')
        category_id = request.args.get('categoryId')
        
        query = Product.query.filter_by(is_active=True)
        
        if search_term:
            query = query.filter(
                or_(
                    Product.name.ilike(f'%{search_term}%'),
                    Product.description.ilike(f'%{search_term}%'),
                    Product.sku.ilike(f'%{search_term}%')
                )
            )
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        products = query.all()
        return jsonify([prod.to_dict() for prod in products]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to search products', 'error': str(e)}), 500 

@products_bp.route('/bulk-upload', methods=['POST'])
@jwt_required()
@roles_required(['manufacturer', 'distributor'])
def bulk_upload_products():
    """Bulk upload products from Excel file"""
    try:
        current_user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'message': 'Please upload an Excel file (.xlsx or .xls)'}), 400
        
        # Read Excel file
        try:
            workbook = openpyxl.load_workbook(file, data_only=True)
            worksheet = workbook.active
            
            # Get headers from first row
            headers = []
            for cell in worksheet[1]:
                headers.append(cell.value.lower() if cell.value else '')
            
            # Validate required columns
            required_columns = ['name', 'sku', 'base_price']
            missing_columns = [col for col in required_columns if col not in headers]
            if missing_columns:
                return jsonify({'message': f'Missing required columns: {", ".join(missing_columns)}'}), 400
            
            added_count = 0
            failed_count = 0
            errors = []
            
            # Process each row starting from row 2
            for row_num in range(2, worksheet.max_row + 1):
                try:
                    row_data = {}
                    for col_num, header in enumerate(headers, 1):
                        cell_value = worksheet.cell(row=row_num, column=col_num).value
                        row_data[header] = cell_value
                    
                    # Validate required fields
                    if not row_data.get('name') or not row_data.get('sku') or not row_data.get('base_price'):
                        errors.append(f"Row {row_num}: Missing required fields")
                        failed_count += 1
                        continue
                    
                    # Check if SKU already exists
                    existing_product = Product.query.filter_by(sku=str(row_data['sku'])).first()
                    if existing_product:
                        errors.append(f"Row {row_num}: SKU '{row_data['sku']}' already exists")
                        failed_count += 1
                        continue
                    
                    # Create new product
                    new_product = Product(
                        name=str(row_data['name']),
                        description=str(row_data.get('description', '')),
                        sku=str(row_data['sku']),
                        category_id=row_data.get('category_id'),
                        manufacturer_id=current_user_id,
                        image_url=row_data.get('image_url'),
                        base_price=float(row_data['base_price']),
                        stock_quantity=int(row_data.get('stock_quantity', 0)),
                        is_active=True
                    )
                    
                    db.session.add(new_product)
                    added_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    failed_count += 1
            
            if added_count > 0:
                db.session.commit()
            
            return jsonify({
                'message': 'Bulk upload completed',
                'added': added_count,
                'failed': failed_count,
                'errors': errors
            }), 200
            
        except Exception as e:
            return jsonify({'message': f'Error reading Excel file: {str(e)}'}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to process bulk upload', 'error': str(e)}), 500 