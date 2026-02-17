# Finance Tracker - Getting Started Guide

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- Plaid account (for bank integration)

### Backend Setup

1. **Clone and navigate**
```bash
cd FinanceTrackerApp/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup database**
```bash
# Create PostgreSQL database
createdb finance_tracker

# Initialize tables
flask db init
flask db migrate
flask db upgrade
```

5. **Configure environment**
Create `.env` file:
```
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=postgresql://localhost/finance_tracker
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=dev-secret-key-change-in-production
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox
```

6. **Run backend**
```bash
python app.py
# API available at http://localhost:5000
```

### Mobile Setup

1. **Navigate to mobile directory**
```bash
cd FinanceTrackerApp/mobile
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
expo start
```

4. **Run on device/emulator**
```bash
# iOS
expo start --ios

# Android
expo start --android
```

### Services Setup

**Redis (for caching & WebSocket)**
```bash
redis-server
```

**Celery (for background tasks)**
```bash
cd backend
celery -A services.celery_tasks worker -l info
```

---

## Testing the App

### Test Endpoints with cURL

**Register User**
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Login**
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Create Transaction**
```bash
curl -X POST http://localhost:5000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "account_id": "account-uuid",
    "amount": 50.00,
    "description": "Grocery store",
    "transaction_date": "2026-02-06T10:30:00Z"
  }'
```

---

## Key Features Walkthrough

### 1. Authentication Flow
```
User → Register → Verify Email → Login → JWT Tokens (Access + Refresh)
```

### 2. Bank Linking (Plaid)
```
User → Click Link Bank → Plaid Modal → Authenticate → Exchange Token
        → Store Access Token → Auto-sync Transactions
```

### 3. Real-time Updates
```
User Opens App → Connect to WebSocket
                 ↓
            Transaction Occurs
                 ↓
            Backend Emits Event → App Updates UI (No Refresh Needed)
```

### 4. Budget Alerts
```
User Sets Budget (e.g., $500/month on Food)
            ↓
    Background Job Checks Daily
            ↓
    Spending ≥ 80% → Send Alert → Push Notification
```

### 5. Bill Reminders
```
Bill Created (Due 15th of month)
            ↓
    3 days before → Send Reminder
            ↓
    After due date → Mark as Overdue
```

---

## Development Workflow

### Backend Development
```bash
# Watch for changes
flask run --reload

# Run tests
pytest tests/

# Check linting
pylint app.py routes/ services/

# Format code
black .
```

### Mobile Development
```bash
# Hot reload enabled by default in Expo

# Build APK (Android)
eas build --platform android --local

# Build IPA (iOS)
eas build --platform ios --local
```

---

## Common Issues & Solutions

### Issue: PostgreSQL connection error
```
Error: could not connect to server
```
**Solution:**
```bash
# Start PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux
```

### Issue: Redis connection error
```
Error: ConnectionRefusedError
```
**Solution:**
```bash
# Start Redis
redis-server
```

### Issue: Plaid token invalid
**Solution:**
- Verify PLAID_CLIENT_ID and PLAID_SECRET in .env
- Ensure PLAID_ENV=sandbox for development
- Create new Plaid account at plaid.com

### Issue: Mobile can't reach backend API
**Solution:**
- Update API_URL in `mobile/src/services/api.ts`
- For iOS simulator: use `http://localhost:5000`
- For Android emulator: use `http://10.0.2.2:5000`
- For physical device: use your machine's IP address

---

## Production Deployment

### Using Docker

**Build image**
```bash
docker build -t finance-tracker:latest .
```

**Run container**
```bash
docker run -e DATABASE_URL=postgresql://... \
           -e REDIS_URL=redis://... \
           -p 5000:5000 \
           finance-tracker:latest
```

### Using AWS/Heroku

**Heroku Deployment**
```bash
heroku create finance-tracker-app
heroku config:set FLASK_ENV=production
git push heroku main
```

### Database Backup
```bash
# Backup
pg_dump finance_tracker > backup.sql

# Restore
psql finance_tracker < backup.sql
```

---

## Monitoring & Logging

### View Backend Logs
```bash
# Real-time logs
tail -f logs/app.log

# Celery logs
tail -f logs/celery.log
```

### Monitor API Health
```bash
curl http://localhost:5000/api/v1/health
```

### WebSocket Debugging
```javascript
// In browser console
socket.on('*', (event) => console.log(event));
```

---

## Next Steps

1. **Customize branding** - Update colors, logos, app name
2. **Add more categories** - Create default transaction categories
3. **Implement notifications** - Push notifications for alerts
4. **Add data export** - PDF reports, CSV export
5. **Setup monitoring** - Sentry for error tracking
6. **Performance tuning** - Database indexes, caching strategies

---

For more detailed information, see [ARCHITECTURE.md](./ARCHITECTURE.md)
