from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Favorite, User
from app.utils.decorators import validate_json

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/', methods=['GET'])
@jwt_required()
def get_favorites():
    """Get user favorites"""
    try:
        current_user_id = get_jwt_identity()
        
        favorites = Favorite.query.filter_by(user_id=current_user_id).all()
        return jsonify([fav.to_dict() for fav in favorites]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch favorites', 'error': str(e)}), 500

@favorites_bp.route('/', methods=['POST'])
@jwt_required()
@validate_json
def add_favorite():
    """Add partner to favorites"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        favorite_user_id = data.get('favoriteUserId')
        favorite_type = data.get('favoriteType')
        
        if not favorite_user_id or not favorite_type:
            return jsonify({'message': 'Favorite user ID and type are required'}), 400
        
        # Check if already favorited
        existing_fav = Favorite.query.filter_by(
            user_id=current_user_id,
            favorite_user_id=favorite_user_id
        ).first()
        
        if existing_fav:
            return jsonify({'message': 'Already in favorites'}), 400
        
        # Verify the favorite user exists
        favorite_user = User.query.get(favorite_user_id)
        if not favorite_user:
            return jsonify({'message': 'User not found'}), 404
        
        new_favorite = Favorite(
            user_id=current_user_id,
            favorite_user_id=favorite_user_id,
            favorite_type=favorite_type
        )
        
        db.session.add(new_favorite)
        db.session.commit()
        
        return jsonify(new_favorite.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add to favorites', 'error': str(e)}), 500

@favorites_bp.route('/<favorite_user_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite(favorite_user_id):
    """Remove partner from favorites"""
    try:
        current_user_id = get_jwt_identity()
        
        favorite = Favorite.query.filter_by(
            user_id=current_user_id,
            favorite_user_id=favorite_user_id
        ).first()
        
        if not favorite:
            return jsonify({'message': 'Favorite not found'}), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({'message': 'Removed from favorites'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to remove from favorites', 'error': str(e)}), 500

@favorites_bp.route('/<favorite_user_id>/check', methods=['GET'])
@jwt_required()
def check_favorite(favorite_user_id):
    """Check if partner is in favorites"""
    try:
        current_user_id = get_jwt_identity()
        
        favorite = Favorite.query.filter_by(
            user_id=current_user_id,
            favorite_user_id=favorite_user_id
        ).first()
        
        return jsonify({'isFavorite': favorite is not None}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to check favorite status', 'error': str(e)}), 500 