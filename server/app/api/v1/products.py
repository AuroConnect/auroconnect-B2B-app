from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.product import Product
from app.models.user import User
from app.models.partnership import PartnerLink
from app import db
from app.utils.decorators import validate_json

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    """Get products based on user role and partnerships"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        
        # Build query based on user role
        query = Product.query
        
        if user.role == 'manufacturer':
            # Manufacturers see only their own products
            query = query.filter(Product.created_by == current_user_id)
            
        elif user.role == 'distributor':
            # Distributors see products from their manufacturer
            manufacturer_link = PartnerLink.get_distributor_manufacturer(current_user_id)
            if manufacturer_link and manufacturer_link.manufacturer_id:
                query = query.filter(Product.created_by == manufacturer_link.manufacturer_id)
            else:
                # If no manufacturer link, return empty results
                query = query.filter(Product.id.is_(None))  # This will return empty results
                
        elif user.role == 'retailer':
            # Retailers see products from their distributor
            distributor_link = PartnerLink.get_retailer_distributor(current_user_id)
            if distributor_link and distributor_link.distributor_id:
                # Get the manufacturer of the distributor to show their products
                distributor_manufacturer_link = PartnerLink.get_distributor_manufacturer(distributor_link.distributor_id)
                if distributor_manufacturer_link and distributor_manufacturer_link.manufacturer_id:
                    query = query.filter(Product.created_by == distributor_manufacturer_link.manufacturer_id)
                else:
                    # If no manufacturer link, return empty results
                    query = query.filter(Product.id.is_(None))
            else:
                # If no distributor link, return empty results
                query = query.filter(Product.id.is_(None))
        
        # Apply category filter
        if category:
            query = query.filter(Product.category == category)
        
        # Apply search filter
        if search:
            query = query.filter(
                Product.name.ilike(f'%{search}%') |
                Product.description.ilike(f'%{search}%')
            )
        
        # Paginate results
        products = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'message': 'Products retrieved successfully',
            'data': {
                'products': [product.to_dict() for product in products.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': products.total,
                    'pages': products.pages,
                    'has_next': products.has_next,
                    'has_prev': products.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/manufacturer', methods=['GET'])
@jwt_required()
def get_manufacturer_products():
    """Get products for distributor dashboard (from their manufacturer)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'distributor':
            return jsonify({'message': 'Access denied'}), 403
        
        # Get distributor's manufacturer
        manufacturer_link = PartnerLink.get_distributor_manufacturer(current_user_id)
        if not manufacturer_link or not manufacturer_link.manufacturer_id:
            return jsonify([]), 200
        
        # Get products from manufacturer
        products = Product.query.filter_by(created_by=manufacturer_link.manufacturer_id).all()
        
        return jsonify([product.to_dict() for product in products]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch manufacturer products', 'error': str(e)}), 500

@products_bp.route('/distributor', methods=['GET'])
@jwt_required()
def get_distributor_products():
    """Get products for retailer dashboard (from their distributor's manufacturer)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'retailer':
            return jsonify({'message': 'Access denied'}), 403
        
        # Get retailer's distributor
        distributor_link = PartnerLink.get_retailer_distributor(current_user_id)
        if not distributor_link or not distributor_link.distributor_id:
            return jsonify([]), 200
        
        # Get distributor's manufacturer
        manufacturer_link = PartnerLink.get_distributor_manufacturer(distributor_link.distributor_id)
        if not manufacturer_link or not manufacturer_link.manufacturer_id:
            return jsonify([]), 200
        
        # Get products from manufacturer
        products = Product.query.filter_by(created_by=manufacturer_link.manufacturer_id).all()
        
        return jsonify([product.to_dict() for product in products]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch distributor products', 'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Get a specific product based on user role and partnerships"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check access based on user role
        if user.role == 'manufacturer':
            # Manufacturers can only see their own products
            if product.created_by != current_user_id:
                return jsonify({'error': 'Product not found'}), 404
                
        elif user.role == 'distributor':
            # Distributors can only see products from their manufacturer
            manufacturer_link = PartnerLink.get_distributor_manufacturer(current_user_id)
            if not manufacturer_link or manufacturer_link.manufacturer_id != product.created_by:
                return jsonify({'error': 'Product not found'}), 404
                
        elif user.role == 'retailer':
            # Retailers can only see products from their distributor's manufacturer
            distributor_link = PartnerLink.get_retailer_distributor(current_user_id)
            if distributor_link and distributor_link.distributor_id:
                distributor_manufacturer_link = PartnerLink.get_distributor_manufacturer(distributor_link.distributor_id)
                if not distributor_manufacturer_link or distributor_manufacturer_link.manufacturer_id != product.created_by:
                    return jsonify({'error': 'Product not found'}), 404
            else:
                return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'message': 'Product retrieved successfully',
            'data': product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/upload-excel', methods=['POST'])
@jwt_required()
def upload_products_excel():
    """Upload products from Excel file"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['manufacturer', 'distributor']:
            return jsonify({'error': 'Only manufacturers and distributors can upload products'}), 403
        
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        # Check file extension
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({'error': 'Invalid file format. Please upload Excel file (.xlsx or .xls)'}), 400
        
        # Try to import pandas
        try:
            import pandas as pd
        except ImportError:
            return jsonify({'error': 'Excel processing not available on server'}), 500
        
        # Read Excel file
        try:
            df = pd.read_excel(file)
        except Exception as e:
            return jsonify({'error': f'Error reading Excel file: {str(e)}'}), 400
        
        # Validate required columns
        required_columns = ['name', 'sku', 'basePrice']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'error': f'Missing required columns: {", ".join(missing_columns)}'}), 400
        
        # Process each row
        created_products = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Generate SKU if not provided
                sku = row.get('sku') or Product.generate_sku()
                
                # Handle price field
                price = row.get('basePrice', 0)
                if isinstance(price, str):
                    price = float(price)
                
                # Handle category field
                category = row.get('category') or row.get('categoryId', 'General')
                
                # Create product
                product = Product(
                    name=row['name'],
                    sku=sku,
                    description=row.get('description', ''),
                    price=price,
                    category=category,
                    created_by=current_user_id,
                    stock=row.get('stock', 0),
                    unit=row.get('unit', 'piece'),
                    is_active=row.get('is_active', True),
                    image_url=row.get('imageUrl')
                )
                
                db.session.add(product)
                created_products.append(product)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        # Commit all products
        try:
            db.session.commit()
            return jsonify({
                'message': f'Successfully uploaded {len(created_products)} products',
                'data': {
                    'created_count': len(created_products),
                    'errors': errors,
                    'products': [product.to_dict() for product in created_products]
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/', methods=['POST'])
@jwt_required()
@validate_json(['name', 'sku', 'basePrice'])
def create_product():
    """Create a new product"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role not in ['manufacturer', 'distributor']:
            return jsonify({'error': 'Only manufacturers and distributors can create products'}), 403
        
        data = request.get_json()
        
        # Generate SKU if not provided
        sku = data.get('sku') or Product.generate_sku()
        
        # Handle price field (frontend sends basePrice, backend expects price)
        price = data.get('basePrice', 0)
        if isinstance(price, str):
            price = float(price)
        
        # Handle category field (frontend sends categoryId, backend expects category)
        category = data.get('category') or data.get('categoryId', 'General')
        
        product = Product(
            name=data['name'],
            sku=sku,
            description=data.get('description', ''),
            price=price,
            category=category,
            created_by=current_user_id,
            stock=data.get('stock_quantity', 0) or data.get('stock', 0),
            unit=data.get('unit', 'piece'),
            is_active=data.get('is_active', True),
            image_url=data.get('imageUrl')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'data': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Update a product"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Only manufacturer or distributor can update their own products
        if user.role not in ['manufacturer', 'distributor'] or product.created_by != current_user_id:
            return jsonify({'error': 'Unauthorized to update this product'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'basePrice' in data:
            price = data['basePrice']
            if isinstance(price, str):
                price = float(price)
            product.price = price
        elif 'price' in data:
            product.price = data['price']
        if 'category' in data:
            product.category = data['category']
        elif 'categoryId' in data:
            product.category = data['categoryId']
        if 'stock' in data:
            product.stock = data['stock']
        elif 'stock_quantity' in data:
            product.stock = data['stock_quantity']
        if 'unit' in data:
            product.unit = data['unit']
        if 'imageUrl' in data:
            product.image_url = data['imageUrl']
        if 'is_active' in data:
            product.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product updated successfully',
            'data': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Delete a product"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Only manufacturer can delete their own products
        if user.role != 'manufacturer' or product.manufacturer_id != current_user_id:
            return jsonify({'error': 'Unauthorized to delete this product'}), 403
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all product categories"""
    try:
        categories = db.session.query(Product.category).distinct().all()
        category_list = [category[0] for category in categories if category[0]]
        
        return jsonify({
            'message': 'Categories retrieved successfully',
            'data': category_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
