"""Main Flask application for Finance Tracker."""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import logging
from datetime import datetime

from config import get_config
from models import db
from routes import auth_bp, transactions_bp, budgets_bp, bills_bp, plaid_bp, analytics_bp
from services.realtime import init_socketio
from services.celery_tasks import celery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)
    socketio = SocketIO(app, cors_allowed_origins="*", message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'])
    
    # Initialize Celery
    celery.conf.update(app.config)
    
    # Initialize WebSocket
    init_socketio(socketio)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info('Database tables created successfully')
    
    return app, socketio


def register_blueprints(app):
    """Register API blueprints."""
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    # app.register_blueprint(accounts_bp, url_prefix='/api/v1/accounts')
    app.register_blueprint(transactions_bp, url_prefix='/api/v1/transactions')
    app.register_blueprint(budgets_bp, url_prefix='/api/v1/budgets')
    app.register_blueprint(bills_bp, url_prefix='/api/v1/bills')
    app.register_blueprint(plaid_bp, url_prefix='/api/v1/plaid')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
    
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'finance-tracker-api'
        }), 200


def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(_):
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid or expired token'}), 401
    
    @app.errorhandler(403)
    def forbidden(_):
        return jsonify({'error': 'Forbidden', 'message': 'You do not have permission to access this resource'}), 403
    
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error('Internal server error: %s', str(error))
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500


def register_cli_commands(app):
    """Register CLI commands."""
    
    @app.cli.command()
    def init_db():
        """Initialize database."""
        db.create_all()
        logger.info('Database initialized successfully')
    
    @app.cli.command()
    def drop_db():
        """Drop all database tables."""
        db.drop_all()
        logger.info('Database dropped successfully')


if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
