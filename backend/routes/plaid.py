"""Plaid bank integration routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import plaid
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from models import db, PlaidConnection, BankAccount

plaid_bp = Blueprint('plaid', __name__)


@plaid_bp.route('/create-link-token', methods=['POST'])
@jwt_required()
def create_link_token():
    """Create Plaid Link token for user."""
    user_id = get_jwt_identity()
    
    try:
        from app import app
        
        client = plaid.ApiClient(
            plaid.Configuration(
                host=plaid.Environment.Sandbox,
                api_key=app.config['PLAID_SECRET'],
                api_version='2020-09-14'
            )
        )
        
        request_data = {
            'user': {'client_user_id': user_id},
            'client_name': 'Finance Tracker',
            'products': [Products('transactions'), Products('auth')],
            'country_codes': [CountryCode('US')],
            'language': 'en'
        }
        
        response = client.link_token_create(request_data)
        
        return jsonify({
            'link_token': response['link_token'],
            'expiration': response['expiration']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@plaid_bp.route('/exchange-token', methods=['POST'])
@jwt_required()
def exchange_token():
    """Exchange public token for access token."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('public_token'):
        return jsonify({'error': 'Missing public_token'}), 400
    
    try:
        from app import app
        
        client = plaid.ApiClient(
            plaid.Configuration(
                host=plaid.Environment.Sandbox,
                api_key=app.config['PLAID_SECRET'],
                api_version='2020-09-14'
            )
        )
        
        response = client.item_public_token_exchange({
            'public_token': data['public_token']
        })
        
        access_token = response['access_token']
        item_id = response['item_id']
        
        plaid_conn = PlaidConnection(
            user_id=user_id,
            access_token=access_token,
            public_token=data['public_token']
        )
        
        db.session.add(plaid_conn)
        db.session.commit()
        
        return jsonify({
            'message': 'Bank account linked successfully',
            'item_id': item_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@plaid_bp.route('/accounts', methods=['GET'])
@jwt_required()
def get_linked_accounts():
    """Get user's linked bank accounts."""
    user_id = get_jwt_identity()
    
    accounts = BankAccount.query.filter_by(user_id=user_id, is_active=True).all()
    
    accounts_data = []
    for account in accounts:
        accounts_data.append({
            'id': account.id,
            'name': account.account_name,
            'bank_name': account.bank_name,
            'account_type': account.account_type,
            'balance': account.balance,
            'currency': account.currency,
            'is_synced': account.is_synced,
            'last_synced_at': account.last_synced_at.isoformat() if account.last_synced_at else None
        })
    
    return jsonify({
        'accounts': accounts_data,
        'total_accounts': len(accounts_data)
    }), 200


@plaid_bp.route('/sync', methods=['POST'])
@jwt_required()
def sync_transactions():
    """Sync transactions from Plaid."""
    user_id = get_jwt_identity()
    
    plaid_conn = PlaidConnection.query.filter_by(user_id=user_id).first()
    
    if not plaid_conn:
        return jsonify({'error': 'No bank account linked'}), 404
    
    try:
        from app import app
        from services.plaid_service import sync_user_transactions
        
        result = sync_user_transactions(user_id, plaid_conn.access_token)
        
        return jsonify({
            'message': 'Transactions synced successfully',
            'synced_count': result.get('synced_count', 0)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@plaid_bp.route('/disconnect', methods=['POST'])
@jwt_required()
def disconnect_account():
    """Disconnect Plaid account."""
    user_id = get_jwt_identity()
    
    plaid_conn = PlaidConnection.query.filter_by(user_id=user_id).first()
    
    if not plaid_conn:
        return jsonify({'error': 'No bank account linked'}), 404
    
    accounts = BankAccount.query.filter_by(user_id=user_id).all()
    for account in accounts:
        account.is_active = False
    
    db.session.delete(plaid_conn)
    db.session.commit()
    
    return jsonify({'message': 'Bank account disconnected'}), 200
