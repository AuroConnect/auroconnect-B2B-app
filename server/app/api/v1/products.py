from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Product, Category, Inventory, User, Partnership
from app.utils.decorators import role_required, roles_required
from sqlalchemy import or_

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    """Get products with role-based visibility"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        print(f"🔍 Fetching products for user {current_user_id} with role {current_user.role if current_user else 'unknown'}")
        
        if not current_user:
            print("❌ User not found")
            return jsonify({'message': 'User not found'}), 404
        
        # Get category filter from query parameters
        category_id = request.args.get('categoryId')
        if category_id:
            print(f"📦 Filtering by category: {category_id}")
        
        # Role-based product visibility
        if current_user.role == 'manufacturer':
            print("🏭 Manufacturer: showing own products")
            query = Product.query.filter_by(
                manufacturer_id=current_user_id,
                is_active=True
            )
        elif current_user.role == 'distributor':
            print("🚚 Distributor: showing manufacturer's products")
            manufacturer_partnership = Partnership.get_distributor_manufacturer(current_user_id)
            if not manufacturer_partnership:
                print("❌ No manufacturer connected")
                return jsonify({'message': 'No manufacturer connected'}), 404
            
            query = Product.query.filter_by(
                manufacturer_id=manufacturer_partnership.manufacturer_id,
                is_active=True
            )
        elif current_user.role == 'retailer':
            print("🏪 Retailer: showing distributor's inventory")
            distributor_partnership = Partnership.get_retailer_distributor(current_user_id)
            if not distributor_partnership:
                print("❌ No distributor connected")
                return jsonify({'message': 'No distributor connected'}), 404
            
            inventory_items = Inventory.query.filter_by(
                distributor_id=distributor_partnership.distributor_id,
                is_available=True
            ).all()
            
            product_ids = [item.product_id for item in inventory_items]
            if not product_ids:
                print("📦 No products in inventory")
                return jsonify([]), 200
            
            query = Product.query.filter(
                Product.id.in_(product_ids),
                Product.is_active == True
            )
        else:
            print(f"❌ Invalid user role: {current_user.role}")
            return jsonify({'message': 'Invalid user role'}), 400
        
        # Apply category filter
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        products = query.all()
        print(f"✅ Found {len(products)} products")
        
        # For retailers, add inventory information
        if current_user.role == 'retailer':
            products_with_inventory = []
            for product in products:
                product_dict = product.to_dict()
                inventory_item = next(
                    (item for item in inventory_items if item.product_id == product.id),
                    None
                )
                if inventory_item:
                    product_dict['inventoryId'] = str(inventory_item.id)
                    product_dict['quantity'] = inventory_item.quantity
                    product_dict['sellingPrice'] = float(inventory_item.selling_price) if inventory_item.selling_price else None
                products_with_inventory.append(product_dict)
            return jsonify(products_with_inventory), 200
        
        return jsonify([prod.to_dict() for prod in products]), 200
        
    except Exception as e:
        print(f"❌ Error fetching products: {e}")
        return jsonify({'message': 'Failed to fetch products', 'error': str(e)}), 500

@products_bp.route('/<product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Get specific product with role-based access control"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Role-based access control
        if current_user.role == 'manufacturer':
            if product.manufacturer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
                
        elif current_user.role == 'distributor':
            manufacturer_partnership = Partnership.get_distributor_manufacturer(current_user_id)
            if not manufacturer_partnership or product.manufacturer_id != manufacturer_partnership.manufacturer_id:
                return jsonify({'message': 'Access denied'}), 403
                
        elif current_user.role == 'retailer':
            distributor_partnership = Partnership.get_retailer_distributor(current_user_id)
            if not distributor_partnership:
                return jsonify({'message': 'Access denied'}), 403
            
            # Check if product is in distributor's inventory
            inventory_item = Inventory.query.filter_by(
                distributor_id=distributor_partnership.distributor_id,
                product_id=product_id,
                is_available=True
            ).first()
            
            if not inventory_item:
                return jsonify({'message': 'Product not available'}), 404
            
            # Add inventory information
            product_dict = product.to_dict()
            product_dict['inventoryId'] = str(inventory_item.id)
            product_dict['quantity'] = inventory_item.quantity
            product_dict['sellingPrice'] = float(inventory_item.selling_price) if inventory_item.selling_price else None
            return jsonify(product_dict), 200
        
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
        current_user = User.query.get(current_user_id)
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
        
        # Determine manufacturer_id based on user role
        manufacturer_id = current_user_id if current_user.role == 'manufacturer' else None
        
        # If distributor is creating product, get their manufacturer
        if current_user.role == 'distributor':
            manufacturer_partnership = Partnership.get_distributor_manufacturer(current_user_id)
            if not manufacturer_partnership:
                return jsonify({'message': 'No manufacturer connected'}), 400
            manufacturer_id = manufacturer_partnership.manufacturer_id
        
        new_product = Product(
            name=data['name'],
            description=data.get('description'),
            sku=data['sku'],
            category_id=data.get('categoryId'),
            manufacturer_id=manufacturer_id,
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
        current_user = User.query.get(current_user_id)
        data = request.get_json()
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Check if user owns this product or has access
        if current_user.role == 'manufacturer':
            if product.manufacturer_id != current_user_id:
                return jsonify({'message': 'Access denied - you can only edit your own products'}), 403
        elif current_user.role == 'distributor':
            manufacturer_partnership = Partnership.get_distributor_manufacturer(current_user_id)
            if not manufacturer_partnership or product.manufacturer_id != manufacturer_partnership.manufacturer_id:
                return jsonify({'message': 'Access denied'}), 403
        
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
        current_user = User.query.get(current_user_id)
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Check if user owns this product or has access
        if current_user.role == 'manufacturer':
            if product.manufacturer_id != current_user_id:
                return jsonify({'message': 'Access denied - you can only delete your own products'}), 403
        elif current_user.role == 'distributor':
            manufacturer_partnership = Partnership.get_distributor_manufacturer(current_user_id)
            if not manufacturer_partnership or product.manufacturer_id != manufacturer_partnership.manufacturer_id:
                return jsonify({'message': 'Access denied'}), 403
        
        # Soft delete by setting is_active to False
        product.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete product', 'error': str(e)}), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        print("🔍 Fetching categories...")
        categories = Category.query.all()
        print(f"✅ Found {len(categories)} categories")
        return jsonify([cat.to_dict() for cat in categories]), 200
        
    except Exception as e:
        print(f"❌ Error fetching categories: {e}")
        return jsonify({'message': 'Failed to fetch categories', 'error': str(e)}), 500

@products_bp.route('/search', methods=['GET'])
@jwt_required()
def search_products():
    """Search products with role-based visibility"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        search_term = request.args.get('q', '')
        category_id = request.args.get('categoryId')
        
        # Use the same role-based query logic as get_products
        if current_user.role == 'manufacturer':
            query = Product.query.filter_by(
                manufacturer_id=current_user_id,
                is_active=True
            )
        elif current_user.role == 'distributor':
            manufacturer_partnership = Partnership.get_distributor_manufacturer(current_user_id)
            if not manufacturer_partnership:
                return jsonify({'message': 'No manufacturer connected'}), 404
            
            query = Product.query.filter_by(
                manufacturer_id=manufacturer_partnership.manufacturer_id,
                is_active=True
            )
        elif current_user.role == 'retailer':
            distributor_partnership = Partnership.get_retailer_distributor(current_user_id)
            if not distributor_partnership:
                return jsonify({'message': 'No distributor connected'}), 404
            
            inventory_items = Inventory.query.filter_by(
                distributor_id=distributor_partnership.distributor_id,
                is_available=True
            ).all()
            
            product_ids = [item.product_id for item in inventory_items]
            if not product_ids:
                return jsonify([]), 200
            
            query = Product.query.filter(
                Product.id.in_(product_ids),
                Product.is_active == True
            )
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        # Apply search filter
        if search_term:
            query = query.filter(
                or_(
                    Product.name.ilike(f'%{search_term}%'),
                    Product.description.ilike(f'%{search_term}%'),
                    Product.sku.ilike(f'%{search_term}%')
                )
            )
        
        # Apply category filter
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        products = query.all()
        
        # For retailers, add inventory information
        if current_user.role == 'retailer':
            products_with_inventory = []
            for product in products:
                product_dict = product.to_dict()
                inventory_item = next(
                    (item for item in inventory_items if item.product_id == product.id),
                    None
                )
                if inventory_item:
                    product_dict['inventoryId'] = str(inventory_item.id)
                    product_dict['quantity'] = inventory_item.quantity
                    product_dict['sellingPrice'] = float(inventory_item.selling_price) if inventory_item.selling_price else None
                products_with_inventory.append(product_dict)
            return jsonify(products_with_inventory), 200
        
        return jsonify([prod.to_dict() for prod in products]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to search products', 'error': str(e)}), 500 