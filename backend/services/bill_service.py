"""Bill reminder service."""
from models import db, Bill
from datetime import datetime, timedelta
from services.realtime import emit_bill_reminder
import logging

logger = logging.getLogger(__name__)


def send_reminders():
    """Send reminders for upcoming bills."""
    try:
        bills = Bill.query.filter(
            Bill.status.in_(['pending', 'overdue'])
        ).all()
        
        reminders_sent = 0
        for bill in bills:
            if bill.next_due_date:
                days_until_due = (bill.next_due_date.date() - datetime.utcnow().date()).days
                
                # Send reminder if due date is within reminder window
                if 0 <= days_until_due <= bill.reminder_days_before:
                    emit_bill_reminder(bill.user_id, {
                        'id': bill.id,
                        'name': bill.name,
                        'amount': bill.amount,
                        'due_date': bill.next_due_date.isoformat(),
                        'days_until_due': days_until_due
                    })
                    reminders_sent += 1
                
                # Mark as overdue if past due date
                if days_until_due < 0 and bill.status != 'overdue':
                    bill.status = 'overdue'
                    db.session.commit()
        
        logger.info('Sent %s bill reminders', reminders_sent)
        return {'reminders_sent': reminders_sent}
        
    except Exception as e:
        logger.error('Error sending bill reminders: %s', str(e))
        raise


def create_bill(user_id, bill_data):
    """Create a new bill reminder."""
    try:
        bill = Bill(
            user_id=user_id,
            name=bill_data['name'],
            description=bill_data.get('description'),
            amount=bill_data['amount'],
            currency=bill_data.get('currency', 'USD'),
            due_date=bill_data['due_date'],
            category=bill_data.get('category'),
            frequency=bill_data['frequency'],
            is_recurring=bill_data.get('is_recurring', True),
            reminder_days_before=bill_data.get('reminder_days_before', 3)
        )
        
        # Calculate next due date
        bill.next_due_date = calculate_next_due_date(bill)
        
        db.session.add(bill)
        db.session.commit()
        
        logger.info('Created bill %s for user %s', bill.id, user_id)
        return bill
        
    except Exception as e:
        logger.error('Error creating bill: %s', str(e))
        raise


def calculate_next_due_date(bill):
    """Calculate next due date for a bill."""
    today = datetime.utcnow()
    
    if bill.frequency == 'monthly':
        if today.day <= bill.due_date:
            return today.replace(day=bill.due_date)
        else:
            # Next month
            if today.month == 12:
                return today.replace(year=today.year + 1, month=1, day=bill.due_date)
            else:
                return today.replace(month=today.month + 1, day=bill.due_date)
    
    elif bill.frequency == 'yearly':
        if today.month < bill.due_date or (today.month == bill.due_date and today.day <= 1):
            return today.replace(month=bill.due_date, day=1)
        else:
            return today.replace(year=today.year + 1, month=bill.due_date, day=1)
    
    elif bill.frequency == 'one_time':
        return bill.next_due_date
    
    return today + timedelta(days=30)


def mark_bill_paid(bill_id):
    """Mark a bill as paid."""
    try:
        bill = Bill.query.get(bill_id)
        if bill:
            bill.is_paid = True
            bill.last_paid_date = datetime.utcnow()
            bill.status = 'paid'
            
            # Calculate next due date if recurring
            if bill.is_recurring:
                bill.next_due_date = calculate_next_due_date(bill)
                bill.is_paid = False
                bill.status = 'pending'
            
            db.session.commit()
            logger.info('Marked bill %s as paid', bill_id)
            return bill
    except Exception as e:
        logger.error('Error marking bill as paid: %s', str(e))
        raise


def delete_bill(bill_id):
    """Delete a bill."""
    try:
        bill = Bill.query.get(bill_id)
        if bill:
            bill.status = 'cancelled'
            db.session.commit()
            logger.info('Deleted bill %s', bill_id)
            return True
    except Exception as e:
        logger.error('Error deleting bill: %s', str(e))
        raise
