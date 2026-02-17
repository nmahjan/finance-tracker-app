"""Budget management service."""
from models import db, Budget, Transaction
from datetime import datetime
from services.realtime import emit_budget_alert
import logging

logger = logging.getLogger(__name__)


def check_budgets(user_id):
    """Check budgets and send alerts if threshold exceeded."""
    try:
        budgets = Budget.query.filter_by(user_id=user_id, is_active=True).all()
        
        alerts_sent = 0
        for budget in budgets:
            # Calculate spent amount for this budget
            spent = calculate_budget_spent(budget)
            budget.spent_amount = spent
            
            percentage = (spent / budget.limit_amount * 100) if budget.limit_amount > 0 else 0
            
            # Send alert if threshold exceeded and not already sent
            if percentage >= budget.alert_threshold and not budget.alert_sent:
                emit_budget_alert(user_id, {
                    'id': budget.id,
                    'name': budget.name,
                    'percentage': round(percentage, 2),
                    'limit': budget.limit_amount,
                    'spent': spent
                })
                budget.alert_sent = True
                alerts_sent += 1
            
            db.session.commit()
        
        logger.info('Sent %s budget alerts for user %s', alerts_sent, user_id)
        return {'alerts_sent': alerts_sent}
        
    except Exception as e:
        logger.error('Error checking budgets: %s', str(e))
        raise


def calculate_budget_spent(budget):
    """Calculate amount spent for a budget."""
    try:
        transactions = Transaction.query.filter(
            Transaction.user_id == budget.user_id,
            Transaction.transaction_type == 'debit',
            Transaction.transaction_date >= budget.start_date,
            Transaction.transaction_date <= budget.end_date
        )
        
        if budget.category_id:
            transactions = transactions.filter_by(category_id=budget.category_id)
        
        spent = sum(t.amount for t in transactions.all())
        return spent
        
    except (ValueError, AttributeError, TypeError) as e:
        logger.error('Error calculating budget spent: %s', str(e))
        return 0


def create_budget(user_id, budget_data):
    """Create a new budget."""
    try:
        budget = Budget(
            user_id=user_id,
            name=budget_data['name'],
            limit_amount=budget_data['limit_amount'],
            period=budget_data['period'],
            start_date=datetime.fromisoformat(budget_data['start_date']),
            end_date=datetime.fromisoformat(budget_data['end_date']),
            category_id=budget_data.get('category_id'),
            alert_threshold=budget_data.get('alert_threshold', 80.0)
        )
        
        db.session.add(budget)
        db.session.commit()
        
        logger.info('Created budget %s for user %s', budget.id, user_id)
        return budget
        
    except Exception as e:
        logger.error('Error creating budget: %s', str(e))
        raise
