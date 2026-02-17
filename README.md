# Finance Tracker - Real-time Personal Finance App

A modern, full-stack personal finance tracking application with real-time updates, bank integration, budget management, and bill reminders.

## ✨ Key Features

### 📊 Dashboard & Analytics
- Real-time financial overview
- Monthly spending trends
- Income vs. expenses visualization
- Budget progress tracking
- Financial reports

### 💳 Transaction Management
- Automatic bank transaction syncing via Plaid
- Manual transaction entry
- Transaction categorization
- Spending search & filtering
- Transaction history

### 💰 Budget Management
- Create custom budgets by category
- Real-time budget tracking
- Automatic alerts at spending thresholds
- Budget performance analytics

### 📋 Bill Reminders
- Schedule recurring & one-time bills
- Automatic reminders (customizable days before due date)
- Mark bills as paid
- Overdue tracking
- Bill payment history

### 🏦 Bank Integration
- Secure Plaid integration
- Connect multiple bank accounts
- Auto-sync transactions
- Real-time balance updates
- Support for checking, savings, and credit card accounts

### 🔔 Real-time Updates
- Live WebSocket notifications
- Instant transaction updates
- Budget alerts
- Bill reminders
- Balance notifications

### 🔐 Security
- JWT authentication
- Secure password hashing
- Plaid token encryption
- HTTPS/TLS support
- CORS protection

---

## 🏗️ Architecture

**Frontend**: React Native (Mobile app)  
**Backend**: Flask with PostgreSQL  
**Real-time**: Socket.IO WebSockets  
**Tasks**: Celery + Redis  
**Bank API**: Plaid  
**State**: Zustand  

For detailed architecture, see [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)

---

## 📋 Prerequisites

- **Python** 3.11 or higher
- **Node.js** 16 or higher
- **PostgreSQL** 12 or higher
- **Redis** 6 or higher
- **Plaid Account** (free sandbox available)

---

## 🚀 Quick Start

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
FLASK_ENV=development
DATABASE_URL=postgresql://localhost/finance_tracker
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-here
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox
EOF

# Initialize database
createdb finance_tracker

# Run Flask app
python app.py
```

Backend runs on `http://localhost:5000`

### Mobile Setup

```bash
# Navigate to mobile
cd mobile

# Install dependencies
npm install

# Start Expo
expo start

# Run on device/emulator
# Press 'i' for iOS or 'a' for Android
```

### Start Supporting Services

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery worker
cd backend && celery -A services.celery_tasks worker -l info
```

---

## 📱 Mobile Screenshots

```
Login Screen → Dashboard → Transaction List → Budget Tracking → Analytics
    ↓
  Register → Personal Profile → Link Bank Account → Bill Reminders
```

**Key Screens:**
- Login/Register
- Dashboard (overview, recent transactions)
- Transactions (list, filter, add)
- Budgets (create, edit, track)
- Bills (schedule, reminders, mark paid)
- Analytics (charts, trends, reports)
- Bank Linking (Plaid integration)
- Profile (settings, preferences)

---

## 🔌 API Documentation

### Authentication
```
POST   /api/v1/auth/register       - Register new user
POST   /api/v1/auth/login          - User login
POST   /api/v1/auth/refresh        - Refresh token
GET    /api/v1/auth/profile        - Get profile
PUT    /api/v1/auth/profile        - Update profile
```

### Transactions
```
GET    /api/v1/transactions        - List transactions
POST   /api/v1/transactions        - Create transaction
GET    /api/v1/transactions/:id    - Get details
PUT    /api/v1/transactions/:id    - Update
DELETE /api/v1/transactions/:id    - Delete
```

### Budgets
```
GET    /api/v1/budgets             - List budgets
POST   /api/v1/budgets             - Create budget
GET    /api/v1/budgets/:id         - Get details
PUT    /api/v1/budgets/:id         - Update
DELETE /api/v1/budgets/:id         - Delete
```

### Bills
```
GET    /api/v1/bills               - List bills
POST   /api/v1/bills               - Create bill
GET    /api/v1/bills/:id           - Get details
PUT    /api/v1/bills/:id           - Update
POST   /api/v1/bills/:id/pay       - Mark paid
DELETE /api/v1/bills/:id           - Delete
```

### Plaid Integration
```
POST   /api/v1/plaid/create-link-token  - Get Plaid link token
POST   /api/v1/plaid/exchange-token     - Exchange public token
GET    /api/v1/plaid/accounts           - List linked accounts
POST   /api/v1/plaid/sync               - Sync transactions
POST   /api/v1/plaid/disconnect         - Disconnect account
```

### Analytics
```
GET    /api/v1/analytics/summary           - Financial summary
GET    /api/v1/analytics/spending-by-category - Category breakdown
GET    /api/v1/analytics/monthly-trend     - Monthly trends
GET    /api/v1/analytics/budget-progress   - Budget progress
```

---

## 🗄️ Database Schema

Key tables:
- **users** - User accounts
- **bank_accounts** - Linked bank accounts
- **transactions** - Financial transactions
- **budgets** - Budget definitions
- **bills** - Bill reminders
- **categories** - Transaction categories
- **plaid_connections** - Plaid integration data

See [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) for full schema.

---

## 🔄 Real-time Features

WebSocket events:
```
Client Events:
  - connect: Initialize connection
  - subscribe_account: Subscribe to account updates

Server Events:
  - connected: Connection confirmed
  - transaction_update: New transaction
  - balance_update: Account balance changed
  - budget_alert: Budget threshold reached
  - bill_reminder: Bill due soon
```

---

## 🔐 Security Features

✅ JWT token-based authentication  
✅ Password hashing with bcrypt  
✅ HTTPS/TLS support  
✅ CORS protection  
✅ Secure Plaid token storage  
✅ Input validation & sanitization  
✅ Rate limiting (ready to implement)  
✅ SQL injection prevention  

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React Native, Expo, Zustand |
| **Backend** | Flask, Flask-CORS, Flask-JWT |
| **Database** | PostgreSQL, SQLAlchemy ORM |
| **Real-time** | Socket.IO, Flask-SocketIO |
| **Async Tasks** | Celery, Redis |
| **Bank API** | Plaid |
| **Deployment** | Docker, Docker Compose |

---

## 🚀 Deployment

### Using Docker

```bash
# Build
docker build -t finance-tracker .

# Run
docker run -p 5000:5000 \
  -e DATABASE_URL=postgresql://... \
  -e PLAID_CLIENT_ID=... \
  finance-tracker
```

### Using Docker Compose

```bash
docker-compose up -d
```

### Cloud Deployment (Heroku)

```bash
heroku create finance-tracker
git push heroku main
```

---

## 📊 Project Structure

```
FinanceTrackerApp/
├── backend/                    # Flask backend
│   ├── app.py                 # Main application
│   ├── models.py              # Database models
│   ├── config.py              # Configuration
│   ├── requirements.txt        # Python deps
│   ├── routes/                # API endpoints
│   │   ├── auth.py
│   │   ├── transactions.py
│   │   ├── budgets.py
│   │   ├── bills.py
│   │   ├── plaid.py
│   │   └── analytics.py
│   └── services/              # Business logic
│       ├── realtime.py        # WebSocket
│       ├── celery_tasks.py    # Background jobs
│       ├── plaid_service.py
│       ├── budget_service.py
│       ├── bill_service.py
│       └── report_service.py
│
├── mobile/                    # React Native app
│   ├── App.tsx               # Root component
│   ├── package.json
│   └── src/
│       ├── screens/          # Screen components
│       ├── services/         # API client
│       ├── store/            # State management
│       ├── components/       # Reusable components
│       └── types/            # TypeScript types
│
└── docs/                      # Documentation
    ├── ARCHITECTURE.md
    └── GETTING_STARTED.md
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Mobile tests
cd mobile
npm test
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 Environment Variables

### Backend (.env)
```
FLASK_ENV=development
DATABASE_URL=postgresql://user:password@localhost:5432/finance_tracker
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret
PLAID_ENV=sandbox
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password
```

### Mobile (.env)
```
EXPO_PUBLIC_API_URL=http://localhost:5000
EXPO_PUBLIC_ENV=development
```

---

## 📚 Documentation

- [Architecture Overview](./docs/ARCHITECTURE.md)
- [Getting Started Guide](./docs/GETTING_STARTED.md)
- [API Documentation](./docs/ARCHITECTURE.md#-api-endpoints)
- [Database Schema](./docs/ARCHITECTURE.md#-database-schema)

---

## 🐛 Known Issues

- [ ] Plaid sandbox mode only (production keys needed for live)
- [ ] Mobile app requires npm dependencies installation
- [ ] Database migrations need manual setup

---

## 🔮 Future Enhancements

- [ ] Multi-currency support
- [ ] Advanced ML-based budget recommendations
- [ ] Tax report generation
- [ ] Investment tracking
- [ ] Family/shared budgets
- [ ] Offline mode for mobile
- [ ] Dark mode UI
- [ ] Custom notifications
- [ ] Export to PDF/Excel
- [ ] Voice commands for transactions

---

## 📄 License

MIT License - See LICENSE file for details

---

## 💬 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check [Getting Started Guide](./docs/GETTING_STARTED.md)
- Review [Architecture Documentation](./docs/ARCHITECTURE.md)

---

**Built with ❤️ for better personal finance management**

Version: 1.0.0  
Last Updated: February 2026
