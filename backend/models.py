"""Database models for Finance Tracker."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


class User(db.Model):
    """User model."""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    profile_picture = db.Column(db.String(500))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    
    # Relationships
    accounts = db.relationship('BankAccount', back_populates='user', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', back_populates='user', cascade='all, delete-orphan')
    budgets = db.relationship('Budget', back_populates='user', cascade='all, delete-orphan')
    bills = db.relationship('Bill', back_populates='user', cascade='all, delete-orphan')
    categories = db.relationship('Category', back_populates='user', cascade='all, delete-orphan')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'


class BankAccount(db.Model):
    """Bank account model."""
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    plaid_account_id = db.Column(db.String(255), unique=True)
    plaid_item_id = db.Column(db.String(255))
    
    account_name = db.Column(db.String(255))
    account_number = db.Column(db.String(20))
    account_type = db.Column(db.String(50))  # checking, savings, credit_card
    bank_name = db.Column(db.String(255))
    
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    
    is_active = db.Column(db.Boolean, default=True)
    is_synced = db.Column(db.Boolean, default=False)
    last_synced_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', back_populates='accounts')
    transactions = db.relationship('Transaction', back_populates='account', cascade='all, delete-orphan')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Category(db.Model):
    """Transaction category model."""
    __tablename__ = 'categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), default='#808080')  # Hex color
    icon = db.Column(db.String(50))  # Icon name/ID
    category_type = db.Column(db.String(20))  # income, expense, transfer
    
    is_default = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', back_populates='categories')
    transactions = db.relationship('Transaction', back_populates='category')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='uq_user_category'),)


class Transaction(db.Model):
    """Transaction model."""
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.String(36), db.ForeignKey('bank_accounts.id'), nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'))
    
    plaid_transaction_id = db.Column(db.String(255), unique=True)
    
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    merchant_name = db.Column(db.String(255))
    
    transaction_type = db.Column(db.String(20))  # debit, credit
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed
    
    transaction_date = db.Column(db.DateTime, nullable=False, index=True)
    posted_date = db.Column(db.DateTime)
    
    is_recurring = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', back_populates='transactions')
    account = db.relationship('BankAccount', back_populates='transactions')
    category = db.relationship('Category', back_populates='transactions')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Budget(db.Model):
    """Budget model."""
    __tablename__ = 'budgets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'))
    
    name = db.Column(db.String(255), nullable=False)
    limit_amount = db.Column(db.Float, nullable=False)
    spent_amount = db.Column(db.Float, default=0.0)
    
    period = db.Column(db.String(20))  # daily, weekly, monthly, yearly
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    alert_threshold = db.Column(db.Float, default=80.0)  # Alert at 80% spent
    alert_sent = db.Column(db.Boolean, default=False)
    
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', back_populates='budgets')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Bill(db.Model):
    """Bill reminder model."""
    __tablename__ = 'bills'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    due_date = db.Column(db.Integer)  # Day of month (1-31)
    category = db.Column(db.String(100))  # e.g., utilities, insurance, subscription
    
    frequency = db.Column(db.String(20))  # monthly, quarterly, yearly, one_time
    is_recurring = db.Column(db.Boolean, default=True)
    
    is_paid = db.Column(db.Boolean, default=False)
    last_paid_date = db.Column(db.DateTime)
    next_due_date = db.Column(db.DateTime, index=True)
    
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue, cancelled
    
    reminder_days_before = db.Column(db.Integer, default=3)  # Remind 3 days before
    is_important = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', back_populates='bills')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlaidConnection(db.Model):
    """Plaid connection model."""
    __tablename__ = 'plaid_connections'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    
    access_token = db.Column(db.String(500), nullable=False)
    public_token = db.Column(db.String(500))
    
    is_active = db.Column(db.Boolean, default=True)
    last_sync = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
