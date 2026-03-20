# 🏗️ CPA Smart Revision - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Browser)                      │
│  ┌──────────────┬──────────────┬────────────┬─────────────┐ │
│  │  Home Page   │   Dashboard  │   Topics   │  Profile    │ │
│  │  (Landing)   │  (Student)   │  (Study)   │  (Settings) │ │
│  └──────────────┴──────────────┴────────────┴─────────────┘ │
│         │                │              │            │       │
│         └────────────────┴──────────────┴────────────┘       │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │ HTTP/AJAX
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    DJANGO APPLICATION                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  URL Router                          │   │
│  └──────────────────────────────────────────────────────┘   │
│           │              │              │           │        │
│  ┌────────▼────┐  ┌──────▼──────┐  ┌───▼────┐  ┌───▼────┐  │
│  │  Accounts   │  │   Content   │  │Revision│  │Subscr. │  │
│  │             │  │             │  │        │  │        │  │
│  │ • Users     │  │ • Levels    │  │• Prog. │  │• Plans │  │
│  │ • Profiles  │  │ • Units     │  │• Sess. │  │• Paym. │  │
│  │ • Auth      │  │ • Topics    │  │• Track │  │• M-Pesa│  │
│  └─────────────┘  └─────────────┘  └────────┘  └────────┘  │
│           │              │              │           │        │
│  ┌────────▼────┐  ┌──────▼──────┐  ┌───▼────────────────┐  │
│  │  AI Tutor   │  │   Planner   │  │    Analytics       │  │
│  │             │  │             │  │                    │  │
│  │ • OpenAI    │  │ • Schedule  │  │ • Progress Stats   │  │
│  │ • Claude    │  │ • Goals     │  │ • Weakness Report  │  │
│  │ • Usage     │  │ • Calendar  │  │ • Time Analysis    │  │
│  └─────────────┘  └─────────────┘  └────────────────────┘  │
│                                                              │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  ┌──────────────────────┐      ┌──────────────────────┐     │
│  │   PostgreSQL DB      │      │    Redis Cache       │     │
│  │                      │      │   (Optional)         │     │
│  │ • User Data          │      │ • AI Responses       │     │
│  │ • Content            │      │ • Session Data       │     │
│  │ • Progress           │      │                      │     │
│  │ • Subscriptions      │      │                      │     │
│  └──────────────────────┘      └──────────────────────┘     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 EXTERNAL SERVICES                            │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐   │
│  │  M-Pesa    │  │  OpenAI    │  │  Email Service      │   │
│  │  (Daraja)  │  │  / Claude  │  │  (SMTP/SendGrid)    │   │
│  └────────────┘  └────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema (Simplified)

```
┌──────────────┐          ┌─────────────────┐
│    User      │──────────│ StudentProfile  │
│              │ 1     1  │                 │
│ • email      │          │ • level         │
│ • password   │          │ • part          │
│ • full_name  │          │ • exam_date     │
└──────┬───────┘          └─────────────────┘
       │
       │ 1
       │
       │ N
┌──────▼──────────┐       ┌──────────────┐
│ Subscription    │───────│ SubPlan      │
│                 │ N   1 │              │
│ • plan          │       │ • name       │
│ • status        │       │ • price      │
│ • expires_at    │       │ • ai_limit   │
└─────────────────┘       └──────────────┘
       │
       │ 1
       │
       │ N
┌──────▼──────────┐
│   Payment       │
│                 │
│ • amount        │
│ • status        │
│ • mpesa_receipt │
└─────────────────┘


┌────────────┐        ┌──────────┐        ┌──────────┐
│   Level    │────────│   Part   │────────│   Unit   │
│            │ 1    N │          │ 1    N │          │
│ • name     │        │ • name   │        │ • code   │
│ • code     │        │ • level  │        │ • name   │
└────────────┘        └──────────┘        └─────┬────┘
                                                 │ 1
                                                 │
                                                 │ N
                                          ┌──────▼──────┐
                                          │    Topic    │
                                          │             │
                                          │ • title     │
                                          │ • content   │
                                          │ • difficulty│
                                          └──────┬──────┘
                                                 │ 1
       ┌─────────────────────────────────────────┤
       │                                         │ N
┌──────▼────────┐                         ┌─────▼────────┐
│ TopicProgress │                         │   Question   │
│               │                         │              │
│ • student     │                         │ • text       │
│ • topic       │                         │ • answer     │
│ • completed   │                         │ • options    │
│ • time_spent  │                         └──────────────┘
└───────────────┘
```

## Data Flow Examples

### 1. User Registration Flow
```
User submits form
    ↓
Django View validates
    ↓
Create User in DB
    ↓
Signal creates StudentProfile
    ↓
Assign Free Subscription
    ↓
Send welcome email
    ↓
Redirect to Dashboard
```

### 2. Topic Study Flow
```
User selects topic
    ↓
Check subscription access
    ↓
Load topic content
    ↓
Track view time
    ↓
User marks complete
    ↓
Update TopicProgress
    ↓
Update UnitProgress
    ↓
Redirect to next topic
```

### 3. AI Question Flow
```
User asks AI question
    ↓
Check usage limit
    ↓
Call OpenAI/Claude API
    ↓
Get response
    ↓
Cache response (Redis)
    ↓
Increment usage counter
    ↓
Return to user
```

### 4. Payment Flow (M-Pesa)
```
User selects plan
    ↓
Create Payment record
    ↓
Call M-Pesa STK Push
    ↓
User enters M-Pesa PIN
    ↓
M-Pesa callback webhook
    ↓
Validate transaction
    ↓
Update Payment status
    ↓
Activate Subscription
    ↓
Send receipt email
```

## Technology Stack

### Backend
- **Framework**: Django 4.2+
- **API**: Django REST Framework
- **Database**: PostgreSQL (Production), SQLite (Dev)
- **Cache**: Redis (Optional)
- **Task Queue**: Celery (Future)

### Frontend
- **Templates**: Django Templates
- **CSS**: Bootstrap 5
- **JS**: Alpine.js (lightweight reactivity)
- **Icons**: Bootstrap Icons

### External Services
- **AI**: OpenAI GPT-4 or Anthropic Claude
- **Payments**: M-Pesa Daraja API, Stripe
- **Email**: SMTP (Gmail/SendGrid)
- **Storage**: Local (Dev), S3 (Production)

### DevOps
- **Server**: Gunicorn
- **Reverse Proxy**: Nginx
- **SSL**: Let's Encrypt
- **Hosting**: Railway/Render/DigitalOcean
- **Monitoring**: Sentry

## Security Architecture

```
┌─────────────────────────────────────┐
│         Security Layers              │
├─────────────────────────────────────┤
│ 1. HTTPS/SSL (Let's Encrypt)        │
│ 2. Django Security Middleware       │
│ 3. CSRF Protection                  │
│ 4. JWT Authentication (API)         │
│ 5. Session-based Auth (Web)         │
│ 6. Password Hashing (PBKDF2)        │
│ 7. Rate Limiting                    │
│ 8. Input Validation                 │
│ 9. SQL Injection Protection         │
│ 10. XSS Protection                  │
└─────────────────────────────────────┘
```

## Scalability Considerations

### Current (MVP)
- Single server
- SQLite/PostgreSQL
- ~1,000 concurrent users

### Phase 2 (Growth)
- Redis caching
- CDN for static files
- Database read replicas
- ~10,000 concurrent users

### Phase 3 (Scale)
- Load balancer
- Multiple app servers
- Separate database server
- Message queue (Celery + RabbitMQ)
- ~100,000 concurrent users

## Deployment Architecture (Production)

```
Internet
    ↓
┌───────────────┐
│ DNS (Domain)  │
└───────┬───────┘
        ↓
┌───────────────┐
│ Load Balancer │
└───────┬───────┘
        ↓
┌───────────────┐
│  Nginx (SSL)  │
└───────┬───────┘
        ↓
┌───────────────┐
│   Gunicorn    │
└───────┬───────┘
        ↓
┌───────────────┐
│ Django App    │
└───────┬───────┘
        │
    ┌───┴────┬──────────┐
    ↓        ↓          ↓
┌────────┐ ┌──────┐ ┌─────────┐
│PostreSQL│ │Redis│ │  S3     │
└────────┘ └──────┘ └─────────┘
```

---

This architecture is designed to:
- ✅ Start simple (single server)
- ✅ Scale incrementally
- ✅ Minimize costs initially
- ✅ Handle growth gracefully
- ✅ Maintain security
- ✅ Support feature additions

Start with the MVP architecture and scale as your user base grows!
