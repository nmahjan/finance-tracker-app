"""Types and interfaces for the mobile app."""

# Authentication
class User:
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    email_verified: bool
    created_at: str


# Transactions
class Transaction:
    id: str
    amount: float
    description: str
    merchant_name: str
    type: str  # debit, credit
    category_id: str
    account_id: str
    transaction_date: str
    status: str
    notes: str


# Budgets
class Budget:
    id: str
    name: str
    limit_amount: float
    spent_amount: float
    period: str  # daily, weekly, monthly, yearly
    percentage_used: float
    status: str  # ok, warning, over
    start_date: str
    end_date: str
    remaining: float
    alert_threshold: float


# Bills
class Bill:
    id: str
    name: str
    description: str
    amount: float
    currency: str
    due_date: int
    frequency: str
    status: str  # pending, paid, overdue, cancelled
    next_due_date: str
    is_important: bool
    reminder_days_before: int
    category: str


# Bank Accounts
class BankAccount:
    id: str
    name: str
    bank_name: str
    account_type: str
    balance: float
    currency: str
    is_synced: bool
    last_synced_at: str


# Analytics
class FinancialSummary:
    period: str
    income: float
    expenses: float
    net: float
    budget: dict
    bills: dict
