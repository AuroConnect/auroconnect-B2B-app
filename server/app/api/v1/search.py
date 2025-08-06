from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import SearchHistory, User
from app.utils.decorators import validate_json

search_bp = Blueprint('search', __name__)

@search_bp.route('/history', methods=['GET'])
@jwt_required()
def get_search_history():
    """Get user search history"""
    try:
        current_user_id = get_jwt_identity()
        limit = request.args.get('limit', 10, type=int)
        
        history = SearchHistory.query.filter_by(user_id=current_user_id)\
            .order_by(SearchHistory.created_at.desc())\
            .limit(limit)\
            .all()
        
        return jsonify([item.to_dict() for item in history]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch search history', 'error': str(e)}), 500

@search_bp.route('/history', methods=['POST'])
@jwt_required()
@validate_json
def add_search_history():
    """Add search to history"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        search_term = data.get('searchTerm')
        search_type = data.get('searchType')
        result_count = data.get('resultCount', 0)
        
        if not search_term or not search_type:
            return jsonify({'message': 'Search term and type are required'}), 400
        
        if search_type not in ['product', 'manufacturer', 'distributor']:
            return jsonify({'message': 'Invalid search type'}), 400
        
        new_search = SearchHistory(
            user_id=current_user_id,
            search_term=search_term,
            search_type=search_type,
            result_count=result_count
        )
        
        db.session.add(new_search)
        db.session.commit()
        
        return jsonify(new_search.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add search history', 'error': str(e)}), 500 