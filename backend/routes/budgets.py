"""Budget routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, Budget, Category, Transaction

budgets_bp = Blueprint('budgets', __name__)


@budgets_bp.route('', methods=['POST'])
@jwt_required()
def create_budget():
    """Create a new budget."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not all(k in data for k in ('name', 'limit_amount', 'period', 'start_date', 'end_date')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    budget = Budget(
        user_id=user_id,
        name=data['name'],
        limit_amount=data['limit_amount'],
        period=data['period'],
        start_date=datetime.fromisoformat(data['start_date']),
        end_date=datetime.fromisoformat(data['end_date']),
        category_id=data.get('category_id'),
        alert_threshold=data.get('alert_threshold', 80.0)
    )
    
    db.session.add(budget)
    db.session.commit()
    
    return jsonify({
        'message': 'Budget created',
        'budget_id': budget.id
    }), 201


@budgets_bp.route('', methods=['GET'])
@jwt_required()
def get_budgets():
    """Get user budgets."""
    user_id = get_jwt_identity()
    
    budgets = Budget.query.filter_by(user_id=user_id, is_active=True).all()
    
    budgets_data = []
    for budget in budgets:
        budget_data = {
            'id': budget.id,
            'name': budget.name,
            'limit_amount': budget.limit_amount,
            'spent_amount': budget.spent_amount,
            'period': budget.period,
            'percentage_used': (budget.spent_amount / budget.limit_amount * 100) if budget.limit_amount > 0 else 0,
            'status': 'over' if budget.spent_amount > budget.limit_amount else 'warning' if budget.spent_amount >= budget.limit_amount * (budget.alert_threshold / 100) else 'ok',
            'start_date': budget.start_date.isoformat(),
            'end_date': budget.end_date.isoformat(),
            'remaining': max(0, budget.limit_amount - budget.spent_amount),
            'alert_threshold': budget.alert_threshold
        }
        budgets_data.append(budget_data)
    
    return jsonify({
        'budgets': budgets_data,
        'total_budgets': len(budgets_data)
    }), 200


@budgets_bp.route('/<budget_id>', methods=['GET'])
@jwt_required()
def get_budget(budget_id):
    """Get budget details."""
    user_id = get_jwt_identity()
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
    
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    return jsonify({
        'id': budget.id,
        'name': budget.name,
        'limit_amount': budget.limit_amount,
        'spent_amount': budget.spent_amount,
        'period': budget.period,
        'percentage_used': (budget.spent_amount / budget.limit_amount * 100) if budget.limit_amount > 0 else 0,
        'remaining': max(0, budget.limit_amount - budget.spent_amount),
        'status': 'over' if budget.spent_amount > budget.limit_amount else 'warning' if budget.spent_amount >= budget.limit_amount * (budget.alert_threshold / 100) else 'ok',
        'start_date': budget.start_date.isoformat(),
        'end_date': budget.end_date.isoformat(),
        'alert_threshold': budget.alert_threshold,
        'created_at': budget.created_at.isoformat()
    }), 200


@budgets_bp.route('/<budget_id>', methods=['PUT'])
@jwt_required()
def update_budget(budget_id):
    """Update budget."""
    user_id = get_jwt_identity()
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
    
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        budget.name = data['name']
    if 'limit_amount' in data:
        budget.limit_amount = data['limit_amount']
    if 'alert_threshold' in data:
        budget.alert_threshold = data['alert_threshold']
    
    db.session.commit()
    
    return jsonify({'message': 'Budget updated'}), 200


@budgets_bp.route('/<budget_id>', methods=['DELETE'])
@jwt_required()
def delete_budget(budget_id):
    """Delete budget."""
    user_id = get_jwt_identity()
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
    
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    budget.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Budget deleted'}), 200
