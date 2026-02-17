"""Celery task queue configuration and tasks."""
from celery import Celery
import logging

logger = logging.getLogger(__name__)

celery = Celery(__name__)


def init_celery(app):
    """Initialize Celery with Flask app."""
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask


@celery.task
def sync_plaid_transactions(user_id):
    """Background task to sync transactions from Plaid."""
    logger.info('Syncing transactions for user %s', user_id)
    try:
        from services.plaid_service import sync_user_transactions
        result = sync_user_transactions(user_id)
        logger.info('Successfully synced transactions: %s', result)
        return result
    except Exception as e:
        logger.error('Failed to sync transactions: %s', str(e))
        raise


@celery.task
def check_budget_alerts(user_id):
    """Background task to check and send budget alerts."""
    logger.info('Checking budget alerts for user %s', user_id)
    try:
        from services.budget_service import check_budgets
        result = check_budgets(user_id)
        logger.info('Budget check completed: %s', result)
        return result
    except Exception as e:
        logger.error('Failed to check budgets: %s', str(e))
        raise


@celery.task
def send_bill_reminders():
    """Background task to send bill reminders."""
    logger.info('Sending bill reminders')
    try:
        from services.bill_service import send_reminders
        result = send_reminders()
        logger.info('Bill reminders sent: %s', result)
        return result
    except Exception as e:
        logger.error('Failed to send bill reminders: %s', str(e))
        raise


@celery.task
def generate_monthly_report(user_id):
    """Background task to generate monthly report."""
    logger.info('Generating monthly report for user %s', user_id)
    try:
        from services.report_service import generate_report
        result = generate_report(user_id)
        logger.info('Report generated: %s', result)
        return result
    except Exception as e:
        logger.error('Failed to generate report: %s', str(e))
        raise
