"""Report generation service."""
from models import Transaction, Budget, Bill
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def generate_report(user_id, period='monthly'):
    """Generate financial report for user."""
    try:
        if period == 'monthly':
            start_date = datetime.utcnow().replace(day=1)
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1) - timedelta(seconds=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1) - timedelta(seconds=1)
        
        elif period == 'yearly':
            start_date = datetime.utcnow().replace(month=1, day=1)
            end_date = start_date.replace(year=start_date.year + 1) - timedelta(seconds=1)
        
        else:  # weekly
            today = datetime.utcnow()
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=7) - timedelta(seconds=1)
        
        # Get transactions
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).all()
        
        # Calculate totals
        income = sum(t.amount for t in transactions if t.transaction_type == 'credit')
        expenses = sum(t.amount for t in transactions if t.transaction_type == 'debit')
        
        # Get budget info
        budgets = Budget.query.filter_by(user_id=user_id, is_active=True).all()
        
        # Get bills
        bills = Bill.query.filter_by(user_id=user_id).all()
        
        report = {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'income': income,
            'expenses': expenses,
            'net': income - expenses,
            'transaction_count': len(transactions),
            'budget_count': len(budgets),
            'bill_count': len(bills),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        logger.info('Generated %s report for user %s', period, user_id)
        return report
        
    except Exception as e:
        logger.error('Error generating report: %s', str(e))
        raise
