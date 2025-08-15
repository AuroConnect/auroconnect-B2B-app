import pandas as pd
import io
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Product, Category, User, ProductAllocation, Inventory
from app.utils.decorators import roles_required, role_required
from sqlalchemy import or_
import openpyxl
from werkzeug.utils import secure_filename
import os

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    """Get all products with inventory info for authenticated users"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        category_id = request.args.get('categoryId')
        
        # Apply role-based product filtering
        if user.role == 'manufacturer':
            # Manufacturers see only their own products
            query = Product.query.filter_by(
                manufacturer_id=current_user_id,
                is_active=True
            )
        elif user.role == 'distributor':
            # Distributors see only products allocated to them by manufacturers
            from app.models.product_allocation import ProductAllocation
            
            # Get allocated product IDs
            allocated_products = db.session.query(ProductAllocation.product_id).filter_by(
                distributor_id=current_user_id,
                is_active=True
            ).subquery()
            
            query = Product.query.filter(
                Product.id.in_(allocated_products),
                Product.is_active == True
            )
        elif user.role == 'retailer':
            # Retailers see all active products (simplified for now)
            # In a real implementation, this would filter by partnerships
            query = Product.query.filter_by(is_active=True)
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        products = query.all()
        products_with_inventory = []
        
        for product in products:
            product_dict = product.to_dict()
            
            # Apply role-based inventory and pricing rules
            if user.role == 'manufacturer':
                # Manufacturers see unlimited stock and base price
                product_dict['availableStock'] = 999  # Unlimited for manufacturers
                product_dict['sellingPrice'] = float(product.base_price) if product.base_price else 0
                product_dict['isAllocated'] = False
                products_with_inventory.append(product_dict)
                    
            elif user.role == 'distributor':
                # Check if this is an allocated product
                allocation = ProductAllocation.query.filter_by(
                    manufacturer_id=product.manufacturer_id,
                    distributor_id=current_user_id,
                    product_id=product.id,
                    is_active=True
                ).first()
                
                if allocation:
                    # This is a manufacturer product allocated to this distributor
                    inventory = Inventory.query.filter_by(
                        distributor_id=current_user_id,
                        product_id=product.id
                    ).first()
                    
                    product_dict['availableStock'] = inventory.quantity if inventory else 0
                    product_dict['sellingPrice'] = float(allocation.selling_price)
                    product_dict['isAllocated'] = True
                    product_dict['allocationId'] = allocation.id
                    product_dict['manufacturerName'] = product.manufacturer.business_name if product.manufacturer else "Unknown"
                    products_with_inventory.append(product_dict)
                    
                # All products in catalog are allocated manufacturer products
                products_with_inventory.append(product_dict)
                    
            elif user.role == 'retailer':
                # Retailers see products from distributors they have partnerships with
                # For now, show all products with basic info (simplified)
                product_dict['availableStock'] = 0  # Will be updated when partnerships are established
                product_dict['sellingPrice'] = float(product.base_price) if product.base_price else 0
                product_dict['isAllocated'] = False
                product_dict['distributorName'] = "Available from Distributors"
                products_with_inventory.append(product_dict)
        
        return jsonify(products_with_inventory), 200
        
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
        
        # Check if SKU already exists for this manufacturer
        existing_product = Product.query.filter_by(
            sku=data['sku'],
            manufacturer_id=current_user_id
        ).first()
        if existing_product:
            return jsonify({'message': 'Product with this SKU already exists for your company'}), 409
        
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
        
        # Handle distributor assignments for manufacturers
        if data.get('assignedDistributors') and isinstance(data['assignedDistributors'], list):
            from app.models.product_allocation import ProductAllocation
            
            for distributor_id in data['assignedDistributors']:
                # Check if distributor exists and is actually a distributor
                distributor = User.query.filter_by(id=distributor_id, role='distributor').first()
                if distributor:
                    allocation = ProductAllocation(
                        manufacturer_id=current_user_id,
                        distributor_id=distributor_id,
                        product_id=new_product.id,
                        selling_price=data.get('basePrice'),  # Use base price as selling price
                        is_active=True
                    )
                    db.session.add(allocation)
            
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
@roles_required(['manufacturer', 'distributor'])
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

@products_bp.route('/categories', methods=['GET', 'POST'])
def categories():
    """Get all categories or create new category"""
    if request.method == 'GET':
        """Get all categories"""
        try:
            categories = Category.query.all()
            return jsonify([cat.to_dict() for cat in categories]), 200
            
        except Exception as e:
            return jsonify({'message': 'Failed to fetch categories', 'error': str(e)}), 500
    
    elif request.method == 'POST':
        """Create new category"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if not data.get('name'):
                return jsonify({'message': 'Category name is required'}), 400
            
            # Check if category already exists
            existing_category = Category.query.filter_by(name=data['name']).first()
            if existing_category:
                return jsonify({'message': 'Category with this name already exists'}), 409
            
            new_category = Category(
                name=data['name'],
                description=data.get('description', '')
            )
            
            db.session.add(new_category)
            db.session.commit()
            
            return jsonify(new_category.to_dict()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Failed to create category', 'error': str(e)}), 500

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
@role_required('manufacturer')
def bulk_upload_products():
    """Bulk upload products from CSV/Excel file"""
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
        required_columns = ['name', 'sku', 'basePrice']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'message': f'Missing required columns: {", ".join(missing_columns)}'}), 400
        
        results = []
        
        for index, row in df.iterrows():
            try:
                # Validate required fields
                if pd.isna(row['name']) or pd.isna(row['sku']) or pd.isna(row['basePrice']):
                    results.append({
                        'row': index + 1,
                        'name': row.get('name', 'N/A'),
                        'status': 'error',
                        'error': 'Missing required fields (name, sku, basePrice)'
                    })
                    continue
                
                # Check if SKU already exists for this manufacturer
                existing_product = Product.query.filter_by(
                    sku=str(row['sku']),
                    manufacturer_id=current_user_id
                ).first()
                if existing_product:
                    results.append({
                        'row': index + 1,
                        'name': row['name'],
                        'status': 'error',
                        'error': f'SKU {row["sku"]} already exists for your company'
                    })
                    continue
                
                # Get category if provided
                category_id = None
                if 'categoryId' in df.columns and not pd.isna(row['categoryId']):
                    category = Category.query.get(str(row['categoryId']))
                    if category:
                        category_id = category.id
                
                # Create product
                new_product = Product(
                    id=str(uuid.uuid4()),
                    name=str(row['name']),
                    description=str(row.get('description', '')),
                    sku=str(row['sku']),
                    category_id=category_id,
                    manufacturer_id=current_user_id,
                    image_url=str(row.get('imageUrl', '')) if not pd.isna(row.get('imageUrl', '')) else None,
                    base_price=float(row['basePrice']),
                    is_active=True
                )
                
                db.session.add(new_product)
                db.session.flush()  # Get the ID without committing
                
                # Handle distributor assignments if provided
                if 'assignedDistributors' in df.columns and not pd.isna(row['assignedDistributors']):
                    distributor_ids = str(row['assignedDistributors']).split(',')
                    for distributor_id in distributor_ids:
                        distributor_id = distributor_id.strip()
                        if distributor_id:
                            distributor = User.query.filter_by(id=distributor_id, role='distributor').first()
                            if distributor:
                                allocation = ProductAllocation(
                                    manufacturer_id=current_user_id,
                                    distributor_id=distributor_id,
                                    product_id=new_product.id,
                                    is_active=True
                                )
                                db.session.add(allocation)
                
                results.append({
                    'row': index + 1,
                    'name': row['name'],
                    'status': 'success',
                    'productId': new_product.id
                })
                
            except Exception as e:
                results.append({
                    'row': index + 1,
                    'name': row.get('name', 'N/A'),
                    'status': 'error',
                    'error': str(e)
                })
        
        # Commit all successful products
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

@products_bp.route('/manufacturers', methods=['GET'])
@jwt_required()
def get_manufacturers():
    """Get all manufacturers for distributor filtering"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if user.role == 'distributor':
            # Get manufacturers who have allocated products to this distributor
            from app.models.product_allocation import ProductAllocation
            
            allocated_manufacturers = db.session.query(User).join(
                ProductAllocation, User.id == ProductAllocation.manufacturer_id
            ).filter(
                ProductAllocation.distributor_id == current_user_id,
                ProductAllocation.is_active == True
            ).distinct().all()
            
            return jsonify([{
                'id': manufacturer.id,
                'businessName': manufacturer.business_name,
                'email': manufacturer.email
            } for manufacturer in allocated_manufacturers])
        else:
            return jsonify({'message': 'Access denied'}), 403
            
    except Exception as e:
        return jsonify({'message': str(e)}), 500 