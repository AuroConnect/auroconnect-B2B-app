from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
    """Create error response"""
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response

def bad_request(message):
    """400 error handler"""
    return error_response(400, message)

def unauthorized(message):
    """401 error handler"""
    return error_response(401, message)

def forbidden(message):
    """403 error handler"""
    return error_response(403, message)

def not_found(message):
    """404 error handler"""
    return error_response(404, message)

def method_not_allowed(message):
    """405 error handler"""
    return error_response(405, message)

def conflict(message):
    """409 error handler"""
    return error_response(409, message)

def internal_error(message):
    """500 error handler"""
    return error_response(500, message)

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return bad_request('Bad request')
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return unauthorized('Unauthorized')
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return forbidden('Forbidden')
    
    @app.errorhandler(404)
    def not_found_error(error):
        return not_found('Resource not found')
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return method_not_allowed('Method not allowed')
    
    @app.errorhandler(409)
    def conflict_error(error):
        return conflict('Conflict')
    
    @app.errorhandler(500)
    def internal_error_handler(error):
        return internal_error('Internal server error')
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {error}')
        return internal_error('An unexpected error occurred') 