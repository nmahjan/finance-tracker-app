"""Analytics and reports routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func
from models import db, Transaction, Budget, Bill, Category

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_financial_summary():
    """Get financial summary."""
    user_id = get_jwt_identity()
    
    # Last 30 days
    start_date = datetime.utcnow() - timedelta(days=30)
    
    # Total income and expenses
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.transaction_date >= start_date
    ).all()
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'credit')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'debit')
    
    # Budget summary
    budgets = Budget.query.filter_by(user_id=user_id, is_active=True).all()
    total_budget_limit = sum(b.limit_amount for b in budgets)
    total_spent = sum(b.spent_amount for b in budgets)
    
    # Bill summary
    bills = Bill.query.filter_by(user_id=user_id).all()
    upcoming_bills = [b for b in bills if b.next_due_date and b.next_due_date > datetime.utcnow()]
    total_upcoming_bills = sum(b.amount for b in upcoming_bills)
    
    return jsonify({
        'period': 'last_30_days',
        'income': total_income,
        'expenses': total_expenses,
        'net': total_income - total_expenses,
        'budget': {
            'limit': total_budget_limit,
            'spent': total_spent,
            'remaining': total_budget_limit - total_spent,
            'percentage_used': (total_spent / total_budget_limit * 100) if total_budget_limit > 0 else 0
        },
        'bills': {
            'upcoming_count': len(upcoming_bills),
            'upcoming_total': total_upcoming_bills
        }
    }), 200


@analytics_bp.route('/spending-by-category', methods=['GET'])
@jwt_required()
def get_spending_by_category():
    """Get spending breakdown by category."""
    user_id = get_jwt_identity()
    
    # Query parameters
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    spending = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('total')
    ).join(
        Category
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'debit',
        Transaction.transaction_date >= start_date
    ).group_by(Category.name).all()
    
    spending_data = [{'category': s[0], 'amount': float(s[1])} for s in spending]
    
    return jsonify({
        'period_days': days,
        'spending': spending_data,
        'total_spending': sum(s['amount'] for s in spending_data)
    }), 200


@analytics_bp.route('/monthly-trend', methods=['GET'])
@jwt_required()
def get_monthly_trend():
    """Get monthly income vs expense trend."""
    user_id = get_jwt_identity()
    
    months = request.args.get('months', 12, type=int)
    
    trends = []
    for i in range(months):
        month_date = datetime.utcnow() - timedelta(days=30 * i)
        month_start = month_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        month_transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= month_start,
            Transaction.transaction_date <= month_end
        ).all()
        
        income = sum(t.amount for t in month_transactions if t.transaction_type == 'credit')
        expenses = sum(t.amount for t in month_transactions if t.transaction_type == 'debit')
        
        trends.insert(0, {
            'month': month_start.strftime('%Y-%m'),
            'income': income,
            'expenses': expenses,
            'net': income - expenses
        })
    
    return jsonify({
        'trends': trends,
        'months': months
    }), 200


@analytics_bp.route('/budget-progress', methods=['GET'])
@jwt_required()
def get_budget_progress():
    """Get budget progress details."""
    user_id = get_jwt_identity()
    
    budgets = Budget.query.filter_by(user_id=user_id, is_active=True).all()
    
    budget_data = []
    for budget in budgets:
        percentage = (budget.spent_amount / budget.limit_amount * 100) if budget.limit_amount > 0 else 0
        
        budget_data.append({
            'id': budget.id,
            'name': budget.name,
            'limit': budget.limit_amount,
            'spent': budget.spent_amount,
            'remaining': max(0, budget.limit_amount - budget.spent_amount),
            'percentage': percentage,
            'status': 'over' if percentage > 100 else 'warning' if percentage >= budget.alert_threshold else 'ok'
        })
    
    return jsonify({
        'budgets': budget_data,
        'total_budgets': len(budget_data),
        'total_limit': sum(b['limit'] for b in budget_data),
        'total_spent': sum(b['spent'] for b in budget_data)
    }), 200
