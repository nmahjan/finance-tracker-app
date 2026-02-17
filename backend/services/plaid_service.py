"""Plaid bank integration service."""
from models import db, BankAccount, Transaction, PlaidConnection
from datetime import datetime, timedelta
import logging
import plaid
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest

logger = logging.getLogger(__name__)


def get_plaid_client(access_token):
    """Get Plaid API client with access token."""
    from app import app
    try:
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,
            api_key=app.config['PLAID_SECRET'],
            api_version='2020-09-14'
        )
        client = plaid.ApiClient(configuration)
        return client
    except Exception as e:
        logger.error('Failed to initialize Plaid client: %s', str(e))
        raise


def sync_user_transactions(user_id):
    """Sync transactions from Plaid for a user."""
    try:
        # Get user's Plaid connection
        plaid_conn = PlaidConnection.query.filter_by(user_id=user_id, is_active=True).first()
        
        if not plaid_conn:
            logger.warning('No active Plaid connection found for user %s', user_id)
            return {'synced_count': 0, 'error': 'No Plaid connection found'}
        
        logger.info('Syncing transactions for user %s', user_id)
        
        client = get_plaid_client(plaid_conn.access_token)
        
        # Get accounts from Plaid
        accounts_data = get_plaid_accounts(client, plaid_conn.access_token)
        
        synced_count = 0
        for account in accounts_data:
            # Store or update bank account
            bank_account = BankAccount.query.filter_by(
                user_id=user_id,
                plaid_account_id=account['account_id']
            ).first()
            
            if not bank_account:
                bank_account = BankAccount(
                    user_id=user_id,
                    plaid_account_id=account['account_id'],
                    plaid_item_id=account.get('item_id'),
                    account_name=account.get('name', account.get('official_name')),
                    account_type=account.get('subtype'),
                    bank_name=account.get('institution_name', 'Unknown Bank'),
                    balance=account.get('balances', {}).get('current', 0),
                    currency=account.get('balances', {}).get('iso_currency_code', 'USD'),
                    is_synced=True,
                    last_synced_at=datetime.utcnow()
                )
                db.session.add(bank_account)
                db.session.flush()
            else:
                bank_account.balance = account.get('balances', {}).get('current', 0)
                bank_account.is_synced = True
                bank_account.last_synced_at = datetime.utcnow()
            
            # Sync transactions for this account
            transactions = get_plaid_transactions(client, plaid_conn.access_token, account['account_id'])
            
            for txn in transactions:
                # Check if transaction already exists
                existing = Transaction.query.filter_by(
                    plaid_transaction_id=txn.get('transaction_id')
                ).first()
                
                if not existing:
                    transaction = Transaction(
                        user_id=user_id,
                        account_id=bank_account.id,
                        plaid_transaction_id=txn.get('transaction_id'),
                        amount=abs(txn.get('amount', 0)),
                        description=txn.get('name', 'Transaction'),
                        merchant_name=txn.get('merchant_name'),
                        transaction_type='debit' if txn.get('amount', 0) > 0 else 'credit',
                        transaction_date=datetime.fromisoformat(txn.get('date')),
                        status='completed'
                    )
                    db.session.add(transaction)
                    synced_count += 1
        
        db.session.commit()
        
        # Update last sync time
        plaid_conn.last_sync = datetime.utcnow()
        db.session.commit()
        
        logger.info('Synced %s transactions for user %s', synced_count, user_id)
        return {'synced_count': synced_count}
        
    except Exception as e:
        logger.error('Error syncing transactions: %s', str(e))
        db.session.rollback()
        raise


def get_plaid_accounts(client, access_token):
    """Get accounts from Plaid API."""
    try:
        request = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(request)
        
        accounts = []
        for account in response['accounts']:
            accounts.append({
                'account_id': account['account_id'],
                'name': account.get('name'),
                'official_name': account.get('official_name'),
                'subtype': account.get('subtype'),
                'type': account.get('type'),
                'balances': account.get('balances', {}),
                'institution_name': response.get('institution', {}).get('name', 'Unknown'),
                'item_id': response.get('item', {}).get('item_id')
            })
        
        logger.info('Retrieved %s accounts from Plaid', len(accounts))
        return accounts
        
    except Exception as e:
        logger.error('Error retrieving Plaid accounts: %s', str(e))
        return []


def get_plaid_transactions(client, access_token, account_id):
    """Get transactions from Plaid for an account."""
    try:
        # Get transactions from last 30 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options={'account_ids': [account_id]}
        )
        
        response = client.transactions_get(request)
        transactions = response.get('transactions', [])
        
        logger.info('Retrieved %s transactions for account %s', len(transactions), account_id)
        return transactions
        
    except Exception as e:
        logger.error('Error retrieving Plaid transactions: %s', str(e))
        return []


def disconnect_plaid_account(user_id):
    """Disconnect Plaid account."""
    try:
        plaid_conn = PlaidConnection.query.filter_by(user_id=user_id).first()
        
        if plaid_conn:
            # Mark Plaid connection as inactive
            plaid_conn.is_active = False
            db.session.commit()
            
            # Mark bank accounts as inactive
            bank_accounts = BankAccount.query.filter_by(user_id=user_id).all()
            for account in bank_accounts:
                account.is_active = False
            
            db.session.commit()
            logger.info('Disconnected Plaid account for user %s', user_id)
            return True
            
    except Exception as e:
        logger.error('Error disconnecting Plaid: %s', str(e))
        raise
