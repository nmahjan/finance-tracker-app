"""Transaction routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, Transaction, BankAccount

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('', methods=['POST'])
@jwt_required()
def create_transaction():
    """Create a new transaction."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not all(k in data for k in ('account_id', 'amount', 'description', 'transaction_date')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify account belongs to user
    account = BankAccount.query.filter_by(id=data['account_id'], user_id=user_id).first()
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    transaction = Transaction(
        user_id=user_id,
        account_id=data['account_id'],
        category_id=data.get('category_id'),
        amount=data['amount'],
        description=data['description'],
        merchant_name=data.get('merchant_name'),
        transaction_type=data.get('transaction_type', 'debit'),
        transaction_date=datetime.fromisoformat(data['transaction_date']),
        notes=data.get('notes')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Transaction created',
        'transaction_id': transaction.id
    }), 201


@transactions_bp.route('', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get user transactions with filtering."""
    user_id = get_jwt_identity()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filters
    account_id = request.args.get('account_id')
    category_id = request.args.get('category_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transaction_type = request.args.get('type')
    
    query = Transaction.query.filter_by(user_id=user_id)
    
    if account_id:
        query = query.filter_by(account_id=account_id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Transaction.transaction_date <= datetime.fromisoformat(end_date))
    
    transactions = query.order_by(Transaction.transaction_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'transactions': [{
            'id': t.id,
            'amount': t.amount,
            'description': t.description,
            'merchant_name': t.merchant_name,
            'type': t.transaction_type,
            'category_id': t.category_id,
            'account_id': t.account_id,
            'transaction_date': t.transaction_date.isoformat(),
            'status': t.status
        } for t in transactions.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': transactions.total,
            'pages': transactions.pages
        }
    }), 200


@transactions_bp.route('/<transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    """Get transaction details."""
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    return jsonify({
        'id': transaction.id,
        'amount': transaction.amount,
        'description': transaction.description,
        'merchant_name': transaction.merchant_name,
        'type': transaction.transaction_type,
        'category_id': transaction.category_id,
        'account_id': transaction.account_id,
        'transaction_date': transaction.transaction_date.isoformat(),
        'status': transaction.status,
        'notes': transaction.notes,
        'created_at': transaction.created_at.isoformat()
    }), 200


@transactions_bp.route('/<transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    """Update transaction."""
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    data = request.get_json()
    
    if 'category_id' in data:
        transaction.category_id = data['category_id']
    if 'notes' in data:
        transaction.notes = data['notes']
    if 'description' in data:
        transaction.description = data['description']
    
    db.session.commit()
    
    return jsonify({'message': 'Transaction updated'}), 200


@transactions_bp.route('/<transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    """Delete transaction."""
    user_id = get_jwt_identity()
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    db.session.delete(transaction)
    db.session.commit()
    
    return jsonify({'message': 'Transaction deleted'}), 200
