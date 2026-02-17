"""Bill reminder routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, Bill

bills_bp = Blueprint('bills', __name__)


@bills_bp.route('', methods=['POST'])
@jwt_required()
def create_bill():
    """Create a new bill reminder."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not all(k in data for k in ('name', 'amount', 'due_date', 'frequency')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    bill = Bill(
        user_id=user_id,
        name=data['name'],
        description=data.get('description'),
        amount=data['amount'],
        currency=data.get('currency', 'USD'),
        due_date=data['due_date'],
        category=data.get('category'),
        frequency=data['frequency'],
        is_recurring=data.get('is_recurring', True),
        reminder_days_before=data.get('reminder_days_before', 3),
        is_important=data.get('is_important', False)
    )
    
    db.session.add(bill)
    db.session.commit()
    
    return jsonify({
        'message': 'Bill created',
        'bill_id': bill.id
    }), 201


@bills_bp.route('', methods=['GET'])
@jwt_required()
def get_bills():
    """Get user bills."""
    user_id = get_jwt_identity()
    
    status = request.args.get('status')
    category = request.args.get('category')
    
    query = Bill.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    
    bills = query.order_by(Bill.next_due_date).all()
    
    bills_data = []
    for bill in bills:
        bills_data.append({
            'id': bill.id,
            'name': bill.name,
            'amount': bill.amount,
            'currency': bill.currency,
            'due_date': bill.due_date,
            'frequency': bill.frequency,
            'status': bill.status,
            'next_due_date': bill.next_due_date.isoformat() if bill.next_due_date else None,
            'is_important': bill.is_important,
            'reminder_days_before': bill.reminder_days_before,
            'category': bill.category
        })
    
    return jsonify({
        'bills': bills_data,
        'total_bills': len(bills_data)
    }), 200


@bills_bp.route('/<bill_id>', methods=['GET'])
@jwt_required()
def get_bill(bill_id):
    """Get bill details."""
    user_id = get_jwt_identity()
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    return jsonify({
        'id': bill.id,
        'name': bill.name,
        'description': bill.description,
        'amount': bill.amount,
        'currency': bill.currency,
        'due_date': bill.due_date,
        'frequency': bill.frequency,
        'status': bill.status,
        'next_due_date': bill.next_due_date.isoformat() if bill.next_due_date else None,
        'last_paid_date': bill.last_paid_date.isoformat() if bill.last_paid_date else None,
        'is_important': bill.is_important,
        'reminder_days_before': bill.reminder_days_before,
        'category': bill.category,
        'created_at': bill.created_at.isoformat()
    }), 200


@bills_bp.route('/<bill_id>', methods=['PUT'])
@jwt_required()
def update_bill(bill_id):
    """Update bill."""
    user_id = get_jwt_identity()
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        bill.name = data['name']
    if 'amount' in data:
        bill.amount = data['amount']
    if 'status' in data:
        bill.status = data['status']
    if 'is_important' in data:
        bill.is_important = data['is_important']
    
    db.session.commit()
    
    return jsonify({'message': 'Bill updated'}), 200


@bills_bp.route('/<bill_id>/pay', methods=['POST'])
@jwt_required()
def mark_bill_paid(bill_id):
    """Mark bill as paid."""
    user_id = get_jwt_identity()
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    bill.is_paid = True
    bill.status = 'paid'
    bill.last_paid_date = datetime.utcnow()
    bill.alert_sent = False
    
    db.session.commit()
    
    return jsonify({'message': 'Bill marked as paid'}), 200


@bills_bp.route('/<bill_id>', methods=['DELETE'])
@jwt_required()
def delete_bill(bill_id):
    """Delete bill."""
    user_id = get_jwt_identity()
    bill = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
    
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    db.session.delete(bill)
    db.session.commit()
    
    return jsonify({'message': 'Bill deleted'}), 200
