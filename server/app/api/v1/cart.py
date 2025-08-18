from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart, CartItem
from app.models.inventory import Inventory
from app import db
from sqlalchemy import and_
from datetime import datetime

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('', methods=['GET'])
@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    """Get user's cart"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get user's cart
        cart = Cart.query.filter_by(user_id=current_user_id).first()
        
        if not cart:
            return jsonify({
                'id': None,
                'items': [],
                'totalItems': 0,
                'totalAmount': 0.0
            }), 200
        
        # Get cart items with product details
        cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
        items_with_details = []
        total_amount = 0.0  # Initialize as float
        
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if product:
                # Get inventory info for pricing based on role hierarchy
                inventory = None
                if user.role == 'distributor':
                    # Distributor sees their own inventory for allocated products
                    from app.models.product_allocation import ProductAllocation
                    allocation = ProductAllocation.query.filter_by(
                        manufacturer_id=product.manufacturer_id,
                        distributor_id=current_user_id,
                        product_id=product.id,
                        is_active=True
                    ).first()
                    
                    if allocation:
                        # This is an allocated manufacturer product
                        # Use product's stock_quantity since it's from manufacturer
                        inventory = None
                        available_stock = product.stock_quantity or 0
                        unit_price = float(allocation.selling_price)
                    else:
                        # This is the distributor's own product
                        inventory = Inventory.query.filter_by(
                            distributor_id=current_user_id,
                            product_id=product.id
                        ).first()
                        available_stock = inventory.quantity if inventory else 0
                        unit_price = product.base_price
                        
                elif user.role == 'retailer':
                    # Retailer sees their linked distributor's inventory
                    from app.models.partnership import Partnership
                    partnership = Partnership.query.filter_by(
                        partner_id=current_user_id,
                        partnership_type='DISTRIBUTOR_RETAILER',
                        status='active'
                    ).first()
                    
                    if partnership and product.manufacturer_id == partnership.requester_id:
                        inventory = Inventory.query.filter_by(
                            distributor_id=partnership.requester_id,
                            product_id=product.id
                        ).first()
                        unit_price = inventory.selling_price if inventory else product.base_price
                    else:
                        unit_price = product.base_price
                
                # Convert to float to avoid decimal issues
                unit_price_float = float(unit_price) if unit_price else 0.0
                item_total = unit_price_float * item.quantity
                total_amount += item_total
                
                items_with_details.append({
                    'id': item.id,
                    'productId': item.product_id,
                    'productName': product.name,
                    'productSku': product.sku,
                    'productImage': product.image_url,
                    'quantity': item.quantity,
                    'unitPrice': unit_price_float,
                    'totalPrice': item_total,
                    'availableStock': available_stock
                })
        
        return jsonify({
            'id': cart.id,
            'items': items_with_details,
            'totalItems': len(items_with_details),
            'totalAmount': total_amount
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch cart', 'error': str(e)}), 500

@cart_bp.route('', methods=['POST'])
@cart_bp.route('/', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add product to cart"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Prevent manufacturers from adding products to cart
        if current_user.role == 'manufacturer':
            return jsonify({'message': 'Manufacturers cannot add products to cart'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        product_id = data.get('productId')
        quantity = int(data.get('quantity', 1))
        
        if not product_id:
            return jsonify({'message': 'Product ID is required'}), 400
        
        # Check if product exists and is available
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        if not product.is_active:
            return jsonify({'message': 'Product is not available'}), 400
        
        # For distributors, check if product is allocated to them
        if current_user.role == 'distributor':
            from app.models.product_allocation import ProductAllocation
            allocation = ProductAllocation.query.filter_by(
                manufacturer_id=product.manufacturer_id,
                distributor_id=current_user_id,
                product_id=product_id,
                is_active=True
            ).first()
            
            if not allocation:
                return jsonify({'message': 'Product is not available to you'}), 403
        
        # Get or create cart for user
        cart = Cart.query.filter_by(user_id=current_user_id).first()
        if not cart:
            cart = Cart(user_id=current_user_id)
            db.session.add(cart)
            db.session.flush()  # Get the cart ID
        
        # Check if item already exists in cart
        existing_item = CartItem.query.filter_by(
            cart_id=cart.id,
            product_id=product_id
        ).first()
        
        if existing_item:
            # Update quantity
            existing_item.quantity += quantity
            existing_item.updated_at = datetime.utcnow()
        else:
            # Create new cart item
            new_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(new_item)
        
        db.session.commit()
        
        return jsonify({'message': 'Product added to cart successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to add product to cart: {str(e)}'}), 500

@cart_bp.route('/update/<item_id>', methods=['PUT'])
@cart_bp.route('/update/<item_id>/', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    """Update cart item quantity"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        quantity = data.get('quantity')
        
        if quantity is None or quantity < 1:
            return jsonify({'message': 'Valid quantity is required'}), 400
        
        # Get cart item and verify ownership
        cart_item = CartItem.query.get(item_id)
        if not cart_item:
            return jsonify({'message': 'Cart item not found'}), 404
        
        cart = Cart.query.get(cart_item.cart_id)
        if not cart or cart.user_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        cart_item.quantity = quantity
        db.session.commit()
        
        return jsonify({'message': 'Cart item updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update cart item', 'error': str(e)}), 500

@cart_bp.route('/remove/<item_id>', methods=['DELETE'])
@cart_bp.route('/remove/<item_id>/', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    """Remove item from cart"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get cart item and verify ownership
        cart_item = CartItem.query.get(item_id)
        if not cart_item:
            return jsonify({'message': 'Cart item not found'}), 404
        
        cart = Cart.query.get(cart_item.cart_id)
        if not cart or cart.user_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({'message': 'Item removed from cart successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to remove item from cart', 'error': str(e)}), 500

@cart_bp.route('/clear', methods=['DELETE'])
@cart_bp.route('/clear/', methods=['DELETE'])
@jwt_required()
def clear_cart():
    """Clear entire cart"""
    try:
        current_user_id = get_jwt_identity()
        
        cart = Cart.query.filter_by(user_id=current_user_id).first()
        if not cart:
            return jsonify({'message': 'Cart is already empty'}), 200
        
        # Remove all cart items
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
        
        return jsonify({'message': 'Cart cleared successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to clear cart', 'error': str(e)}), 500
