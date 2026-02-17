"""Package init for routes."""
from .auth import auth_bp
from .accounts import accounts_bp
from .transactions import transactions_bp
from .budgets import budgets_bp
from .bills import bills_bp
from .plaid import plaid_bp
from .analytics import analytics_bp

__all__ = [
    'auth_bp',
    'accounts_bp',
    'transactions_bp',
    'budgets_bp',
    'bills_bp',
    'plaid_bp',
    'analytics_bp'
]
