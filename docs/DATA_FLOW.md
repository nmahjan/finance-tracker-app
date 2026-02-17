# Finance Tracker - Data Flow & Integration Guide

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTIONS                                    │
└─────────────────────────────────────────────────────────────────────────────┘

AUTHENTICATION FLOW:
User (Mobile) → Register/Login → Backend Auth API → PostgreSQL
                    ↓
              JWT Token → Secure Store
                    ↓
         All Future Requests Include Token

TRANSACTION FLOW (Manual Entry):
User → Transaction Form → API POST → Validate → Save to DB → Emit WebSocket
                                                                    ↓
                                           Connected Users Receive Update

TRANSACTION FLOW (Bank Import):
User → Link Bank → Plaid Modal → Exchange Token → Store → Sync Task
                                                             ↓
                                        Fetch from Plaid → Parse → Save → Notify

REAL-TIME UPDATE FLOW:
Backend Event (Transaction/Balance/Budget) → WebSocket Emit → Connected Clients
                                                                       ↓
                                                          App Updates UI Instantly

BUDGET TRACKING FLOW:
User Creates Budget → Background Job Runs → Calculate Spending → Check Threshold
                                                                         ↓
                                                    Threshold Met? → Send Alert

BILL REMINDER FLOW:
User Creates Bill → Celery Beat Scheduler → Daily Check → Days Until Due?
                                                    ↓
                                        Remind If Within Window → Send Alert
```

---

## 🏗️ Architecture Layers

```
┌───────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                         │
│              (React Native Mobile App)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Screens: Auth, Dashboard, Transactions, Budgets,   │   │
│  │  Bills, Analytics, Profile, Bank Linking           │   │
│  │                                                      │   │
│  │  State Management: Zustand                          │   │
│  │  HTTP Client: Axios + WebSocket                     │   │
│  └──────────────────────────────────────────────────────┘   │
└────────┬────────────────────────────────────────────────────┘
         │ REST API + WebSocket
         ▼
┌───────────────────────────────────────────────────────────────┐
│                     API LAYER                                 │
│               (Flask REST Endpoints)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /auth - Authentication                             │   │
│  │  /transactions - Transaction CRUD                   │   │
│  │  /budgets - Budget Management                       │   │
│  │  /bills - Bill Reminders                            │   │
│  │  /plaid - Bank Integration                          │   │
│  │  /analytics - Reports & Analytics                   │   │
│  │  WebSocket Events - Real-time Updates               │   │
│  └──────────────────────────────────────────────────────┘   │
└────────┬────────────────────────────────────────────────────┘
         │ Python/ORM
         ▼
┌───────────────────────────────────────────────────────────────┐
│                 BUSINESS LOGIC LAYER                          │
│              (Services & Background Jobs)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  realtime.py - WebSocket Management                 │   │
│  │  celery_tasks.py - Async Tasks                      │   │
│  │  plaid_service.py - Bank Integration                │   │
│  │  budget_service.py - Budget Logic                   │   │
│  │  bill_service.py - Bill Logic                       │   │
│  │  report_service.py - Analytics                      │   │
│  └──────────────────────────────────────────────────────┘   │
└────────┬────────────────────────────────────────────────────┘
         │ SQLAlchemy ORM
         ▼
┌───────────────────────────────────────────────────────────────┐
│                  DATA ACCESS LAYER                            │
│              (SQLAlchemy Models)                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  User, BankAccount, Transaction, Category,          │   │
│  │  Budget, Bill, PlaidConnection                      │   │
│  └──────────────────────────────────────────────────────┘   │
└────────┬────────────────────────────────────────────────────┘
         │ SQL Queries
         ▼
┌───────────────────────────────────────────────────────────────┐
│                  DATABASE LAYER                               │
│             (PostgreSQL + Redis Cache)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PostgreSQL: Persistent Data Storage                │   │
│  │  Redis: Cache, Task Queue, WebSocket Messages       │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

---

## 🔌 Integration Points

### Plaid Bank Integration
```
Mobile App
    ↓
[Link Bank Button]
    ↓
Create Plaid Link Token
    ↓
User Authenticates with Bank
    ↓
Exchange Public Token → Access Token
    ↓
Store in PlaidConnection Table
    ↓
Fetch Accounts & Transactions
    ↓
Save to BankAccount & Transaction Tables
    ↓
Auto-sync Daily (Celery Task)
```

### Real-time Updates System
```
Database Update
    ↓
Service Emits Event
    ↓
WebSocket Broadcast
    ↓
Connected Clients Receive
    ↓
App State Updates (Zustand)
    ↓
UI Re-renders Automatically
```

### Background Job Processing
```
Celery Beat (Scheduler)
    ↓
Check Tasks (Bill Reminders, Budget Alerts)
    ↓
Create Task
    ↓
Celery Worker Process
    ↓
Execute Task
    ↓
Update Database
    ↓
Emit WebSocket Event
    ↓
Notify Users
```

---

## 📊 Request/Response Flow Examples

### Example 1: User Login
```
CLIENT                          SERVER                          DATABASE
  │                               │                                │
  ├─ POST /auth/login ──────────>│                                │
  │  { email, password }          │                                │
  │                               ├─ Query User ──────────────────>│
  │                               │                                │
  │                               │<─ User Data ──────────────────┤
  │                               │                                │
  │                               ├─ Verify Password              │
  │                               │                                │
  │                               ├─ Generate JWT Token           │
  │                               │                                │
  │<─ 200 OK ─────────────────────┤                                │
  │  { accessToken, refreshToken, │                                │
  │    user }                     │                                │
  │                               │                                │
```

### Example 2: Real-time Transaction Update
```
MOBILE APP 1          MOBILE APP 2          SERVER            DATABASE
     │                     │                    │                  │
     ├─ POST /transactions >│                    │                  │
     │ { amount, desc }     │                    ├─ Save ──────────>│
     │                      │                    │                  │
     │                      │<── WebSocket ──────┤<─ Confirm ───────┤
     │                      │  { transaction_    │
     │                      │    update }        │
     │                      │                    │
     │<── WebSocket ────────┤                    │
     │   { transaction_     │                    │
     │     update }         │                    │
     │                      │                    │
  (UI updates)           (UI updates)                              
```

### Example 3: Budget Alert Flow
```
DATABASE UPDATE (spending increased)
    ↓
Budget Service Checks Threshold
    ↓
Spending ≥ 80% of $500 budget
    ↓
Celery Task Creates Alert
    ↓
WebSocket Emits Event
    ↓
Mobile App Receives
    ↓
Show Notification
    ↓
Update Dashboard Display
```

---

## 🔐 Security Layers

```
┌─ TLS/HTTPS ─────────────────────────────────┐
│  All data in transit is encrypted          │
└──────────────────────┬──────────────────────┘
                       ▼
┌─ JWT Token Auth ────────────────────────────┐
│  Every request includes Authorization       │
│  header with Bearer token                   │
└──────────────────────┬──────────────────────┘
                       ▼
┌─ Input Validation ──────────────────────────┐
│  All inputs validated on server side        │
│  Prevents SQL injection, XSS                │
└──────────────────────┬──────────────────────┘
                       ▼
┌─ Password Hashing ──────────────────────────┐
│  Bcrypt hashing of all passwords            │
│  Never stored in plain text                 │
└──────────────────────┬──────────────────────┘
                       ▼
┌─ Plaid Token Encryption ────────────────────┐
│  Bank tokens stored securely                │
│  Never exposed to client                    │
└──────────────────────┬──────────────────────┘
                       ▼
┌─ CORS Protection ───────────────────────────┐
│  Only trusted origins can access API        │
└─────────────────────────────────────────────┘
```

---

## 📈 Scaling Architecture

```
Current Setup (Single Server):
┌─────────────┐
│   Flask     │  + PostgreSQL + Redis
│   Gunicorn  │
└─────────────┘

Scaled Setup (Production):
┌──────────────────────────────────────────────────┐
│              Load Balancer (NGINX)               │
└──────────────────────────────────────────────────┘
         │           │           │
         ▼           ▼           ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │ Flask  │ │ Flask  │ │ Flask  │
    │  App   │ │  App   │ │  App   │
    └────────┘ └────────┘ └────────┘
         │           │           │
         └───────────┼───────────┘
                     ▼
         ┌──────────────────────────┐
         │  PostgreSQL (Replicated) │
         │  Redis Cluster           │
         │  Celery Workers (x5)     │
         │  Celery Beat Scheduler   │
         └──────────────────────────┘
```

---

## 🎯 Feature Timeline

### Phase 1: Core (✅ Implemented)
- Authentication
- Transaction management
- Budget tracking
- Bill reminders
- Bank linking (Plaid)
- Real-time updates
- Analytics

### Phase 2: Enhancement (Ready to build)
- Advanced reporting
- Recurring transactions
- Multiple currencies
- Custom categories
- Import/Export
- Notifications

### Phase 3: AI Features (Architecture ready)
- Budget recommendations
- Spending predictions
- Anomaly detection
- Tax optimization
- Investment tracking

---

## 🚀 Deployment Architecture

### Local Development
```
docker-compose up -d
→ PostgreSQL, Redis, Flask API, Celery
→ All running on localhost
```

### Staging (Docker)
```
AWS EC2 / Digital Ocean
→ Docker containers
→ RDS for database
→ ElastiCache for Redis
```

### Production (Kubernetes Ready)
```
AWS EKS / GCP GKE
→ Multiple Flask pods
→ CloudSQL database
→ Redis cluster
→ CDN for static assets
```

---

## 📱 Mobile State Management

```
Zustand Store (AuthStore)
    │
    ├─ isAuthed (boolean)
    ├─ user (User object)
    ├─ accessToken (string)
    ├─ refreshToken (string)
    │
    └─ Actions:
         ├─ login()
         ├─ register()
         ├─ logout()
         ├─ initAuth()
         └─ setUser()

Usage in Components:
    const user = useAuthStore(state => state.user)
    const login = useAuthStore(state => state.login)
    
    (Reactive: updates trigger re-renders)
```

---

## 🔌 WebSocket Events Reference

### Available Events

**Client → Server:**
```
connect: Establish connection
subscribe_account: Subscribe to account updates
```

**Server → Client:**
```
connected: Confirmation
transaction_update: {
  id, amount, description, date, account_id
}
balance_update: {
  account_id, balance, timestamp
}
budget_alert: {
  budget_id, name, percentage, threshold
}
bill_reminder: {
  bill_id, name, amount, due_date, days_until_due
}
```

---

## 🎓 Learning Resources

**Architecture Concepts:**
- REST API Design
- WebSocket Real-time Systems
- Microservices Patterns
- Database Design & Optimization

**Technologies Used:**
- Flask Web Framework
- SQLAlchemy ORM
- PostgreSQL
- Redis
- Socket.IO
- Celery Task Queue
- React Native
- Zustand State Management

**Key Patterns Implemented:**
- MVC Architecture
- Repository Pattern
- Service Layer Pattern
- Observer Pattern (WebSocket)
- Job Queue Pattern (Celery)

---

## ✅ Quality Assurance

**Implemented:**
- ✅ Input validation on all endpoints
- ✅ Error handling & logging
- ✅ Database transaction management
- ✅ Token refresh mechanism
- ✅ CORS configuration
- ✅ Rate limiting ready
- ✅ Health check endpoint

**Ready to Add:**
- Unit tests
- Integration tests
- Load testing
- Monitoring (Sentry)
- APM (New Relic, DataDog)

---

**This is a complete, production-grade architecture ready for deployment!** 🚀
