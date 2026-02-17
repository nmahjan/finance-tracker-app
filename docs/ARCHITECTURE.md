# Finance Tracker - Full-Stack Architecture

## 🏗️ System Overview

A real-time personal finance tracking application built with:
- **Backend**: Flask + PostgreSQL + WebSockets
- **Mobile**: React Native (Expo)
- **Bank Integration**: Plaid API
- **Real-time Updates**: Socket.IO
- **Task Queue**: Celery + Redis
- **State Management**: Zustand

---

## 📋 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FINANCE TRACKER APP                       │
└─────────────────────────────────────────────────────────────┘

                            ┌─────────────────────┐
                            │   MOBILE APP        │
                            │  (React Native)     │
                            │  - Dashboard        │
                            │  - Transactions     │
                            │  - Budgets          │
                            │  - Bills            │
                            │  - Analytics        │
                            └──────────┬──────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                │                      │                      │
                ▼                      ▼                      ▼
         ┌──────────────┐     ┌─────────────────┐    ┌──────────────┐
         │ REST API     │     │  WebSocket      │    │  Plaid API   │
         │ (Flask)      │     │  (Socket.IO)    │    │  (Bank Sync) │
         └──────┬───────┘     └────────┬────────┘    └──────┬───────┘
                │                      │                      │
                └──────────────┬───────┴──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Backend Server    │
                    │      (Flask)        │
                    └──────┬──────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    ┌────────┐      ┌──────────┐     ┌──────────────┐
    │   DB   │      │  Cache   │     │ Task Queue   │
    │PostgreSQL      │  Redis   │     │  (Celery)    │
    └────────┘      └──────────┘     └──────────────┘
```

---

## 🗂️ Project Structure

```
FinanceTrackerApp/
├── backend/                        # Flask backend
│   ├── app.py                     # Main Flask app
│   ├── config.py                  # Configuration
│   ├── models.py                  # Database models
│   ├── requirements.txt            # Python dependencies
│   ├── routes/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py               # Authentication
│   │   ├── transactions.py        # Transactions management
│   │   ├── budgets.py            # Budget endpoints
│   │   ├── bills.py              # Bill reminders
│   │   ├── plaid.py              # Bank integration
│   │   └── analytics.py          # Reports & analytics
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── realtime.py           # WebSocket service
│   │   ├── celery_tasks.py       # Background jobs
│   │   ├── plaid_service.py      # Plaid integration
│   │   ├── budget_service.py     # Budget calculations
│   │   ├── bill_service.py       # Bill reminders
│   │   └── report_service.py     # Report generation
│   └── utils/                    # Utilities
│
├── mobile/                        # React Native mobile app
│   ├── App.tsx                   # Root component
│   ├── package.json              # Dependencies
│   ├── src/
│   │   ├── screens/              # Screen components
│   │   │   ├── auth/
│   │   │   │   ├── LoginScreen.tsx
│   │   │   │   └── RegisterScreen.tsx
│   │   │   ├── dashboard/
│   │   │   ├── transactions/
│   │   │   ├── budgets/
│   │   │   ├── bills/
│   │   │   ├── analytics/
│   │   │   ├── profile/
│   │   │   └── plaid/
│   │   ├── components/           # Reusable components
│   │   ├── services/             # API & services
│   │   │   └── api.ts           # API client
│   │   ├── store/                # State management
│   │   │   └── authStore.ts     # Auth store
│   │   └── types/                # TypeScript types
│   │       └── index.py
│   └── assets/                   # Images, fonts
│
└── docs/                         # Documentation
```

---

## 🗄️ Database Schema

### Users Table
```
users:
  - id (UUID, PK)
  - email (VARCHAR, UNIQUE)
  - username (VARCHAR, UNIQUE)
  - password_hash
  - first_name, last_name
  - email_verified (BOOL)
  - two_factor_enabled (BOOL)
  - created_at, updated_at
```

### Bank Accounts Table
```
bank_accounts:
  - id (UUID, PK)
  - user_id (FK)
  - plaid_account_id (UNIQUE)
  - account_name, bank_name
  - account_type (checking, savings, credit_card)
  - balance, currency
  - is_synced, last_synced_at
  - created_at, updated_at
```

### Transactions Table
```
transactions:
  - id (UUID, PK)
  - user_id (FK)
  - account_id (FK)
  - category_id (FK)
  - amount, description
  - merchant_name
  - transaction_type (debit, credit)
  - transaction_date, posted_date
  - status (pending, completed, failed)
  - is_recurring, notes
  - created_at, updated_at
```

### Budgets Table
```
budgets:
  - id (UUID, PK)
  - user_id (FK)
  - category_id (FK)
  - name, limit_amount
  - spent_amount
  - period (daily, weekly, monthly, yearly)
  - start_date, end_date
  - alert_threshold, alert_sent
  - is_active
  - created_at, updated_at
```

### Bills Table
```
bills:
  - id (UUID, PK)
  - user_id (FK)
  - name, description
  - amount, currency
  - due_date (day of month)
  - category, frequency
  - is_recurring, is_paid
  - last_paid_date, next_due_date
  - status (pending, paid, overdue, cancelled)
  - reminder_days_before
  - created_at, updated_at
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/profile` - Get user profile
- `PUT /api/v1/auth/profile` - Update profile
- `POST /api/v1/auth/logout` - Logout

### Transactions
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions` - List transactions (paginated, filterable)
- `GET /api/v1/transactions/:id` - Get transaction details
- `PUT /api/v1/transactions/:id` - Update transaction
- `DELETE /api/v1/transactions/:id` - Delete transaction

### Budgets
- `POST /api/v1/budgets` - Create budget
- `GET /api/v1/budgets` - List budgets
- `GET /api/v1/budgets/:id` - Get budget details
- `PUT /api/v1/budgets/:id` - Update budget
- `DELETE /api/v1/budgets/:id` - Delete budget

### Bills
- `POST /api/v1/bills` - Create bill reminder
- `GET /api/v1/bills` - List bills
- `GET /api/v1/bills/:id` - Get bill details
- `PUT /api/v1/bills/:id` - Update bill
- `POST /api/v1/bills/:id/pay` - Mark as paid
- `DELETE /api/v1/bills/:id` - Delete bill

### Plaid Integration
- `POST /api/v1/plaid/create-link-token` - Create Plaid link token
- `POST /api/v1/plaid/exchange-token` - Exchange public token
- `GET /api/v1/plaid/accounts` - Get linked accounts
- `POST /api/v1/plaid/sync` - Sync transactions
- `POST /api/v1/plaid/disconnect` - Disconnect bank account

### Analytics
- `GET /api/v1/analytics/summary` - Financial summary
- `GET /api/v1/analytics/spending-by-category` - Category breakdown
- `GET /api/v1/analytics/monthly-trend` - Monthly trend
- `GET /api/v1/analytics/budget-progress` - Budget progress

---

## 🔄 Real-time Features (WebSocket)

### Events
```
Client → Server:
  - connect: Initial connection
  - subscribe_account: Subscribe to account updates

Server → Client:
  - connected: Confirmation of connection
  - transaction_update: New transaction
  - balance_update: Account balance changed
  - budget_alert: Budget threshold reached
  - bill_reminder: Bill due soon
```

### Usage
```typescript
socket.on('transaction_update', (data) => {
  // Handle real-time transaction update
  console.log('New transaction:', data);
});

socket.on('budget_alert', (data) => {
  // Handle budget alert
  console.log('Budget alert:', data);
});
```

---

## 🔐 Security Features

1. **JWT Authentication**
   - Access tokens (24-hour expiry)
   - Refresh tokens (30-day expiry)
   - Secure token storage

2. **Password Security**
   - Bcrypt hashing
   - Password reset flow

3. **Data Encryption**
   - HTTPS/TLS in production
   - Secure Plaid token storage

4. **CORS Configuration**
   - Whitelist trusted origins
   - Rate limiting

5. **Input Validation**
   - Marshmallow schemas
   - SQL injection prevention

---

## 📱 Mobile Features

1. **Authentication**
   - Login/Register screens
   - Secure token management
   - Biometric login support

2. **Dashboard**
   - Real-time balance display
   - Recent transactions feed
   - Budget overview
   - Upcoming bills widget

3. **Transaction Management**
   - List/filter transactions
   - Add manual transactions
   - Categorize transactions
   - Search functionality

4. **Budget Management**
   - Create/edit budgets
   - Visual progress indicators
   - Alert notifications
   - Category-based budgets

5. **Bill Reminders**
   - Schedule bills
   - Mark as paid
   - Overdue tracking
   - Recurring bills

6. **Bank Integration**
   - Link bank accounts via Plaid
   - Auto-sync transactions
   - Multi-account support

7. **Analytics**
   - Spending charts
   - Monthly trends
   - Category breakdown
   - Financial reports

---

## 🚀 Deployment

### Backend Deployment (Docker)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "app:app"]
```

### Mobile Deployment
```bash
# EAS Build for iOS/Android
eas build --platform ios
eas build --platform android

# Submission
eas submit --platform ios
eas submit --platform android
```

### Production Checklist
- [ ] Environment variables configured
- [ ] Database backups enabled
- [ ] Redis cache configured
- [ ] Celery worker running
- [ ] Plaid production keys set
- [ ] HTTPS/SSL enabled
- [ ] Logging and monitoring
- [ ] Rate limiting enabled
- [ ] CORS configured

---

## 📊 Tech Stack Summary

| Component | Technology |
|-----------|------------|
| Backend | Flask, Flask-SQLAlchemy, Flask-JWT |
| Database | PostgreSQL |
| Real-time | Socket.IO, Flask-SocketIO |
| Task Queue | Celery, Redis |
| Mobile | React Native, Expo, Zustand |
| HTTP Client | Axios |
| Bank API | Plaid |
| Authentication | JWT |
| Containerization | Docker |

---

## 🔧 Installation & Setup

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export FLASK_ENV=development
flask run
```

### Mobile Setup
```bash
cd mobile
npm install
expo start
```

---

## 📝 Environment Variables

### Backend (.env)
```
FLASK_ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/finance_tracker
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
PLAID_CLIENT_ID=your-plaid-client-id
PLAID_SECRET=your-plaid-secret
PLAID_ENV=sandbox
```

---

## 🎯 Future Enhancements

- [ ] Multi-currency support
- [ ] Advanced ML-based budget recommendations
- [ ] Tax report generation
- [ ] Investment tracking
- [ ] Family/shared budgets
- [ ] Mobile app offline support
- [ ] Dark mode
- [ ] Custom alerts and notifications
- [ ] Export data (PDF, Excel)
- [ ] API rate limiting dashboard

---

## 📚 Additional Resources

- Plaid Documentation: https://plaid.com/docs
- Flask Documentation: https://flask.palletsprojects.com
- React Native Docs: https://reactnative.dev
- Socket.IO Guide: https://socket.io/docs

---

**Version**: 1.0.0  
**Last Updated**: February 2026
