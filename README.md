# 🎓 CPA Smart Revision SaaS

A cloud-based CPA revision and AI-powered study assistant platform for KASNEB students in Kenya and East Africa.

## 🚀 Project Overview

**CPA Smart Revision** is a comprehensive SaaS platform designed specifically for Certified Public Accountants (CPA) students preparing for KASNEB examinations. The platform provides:

- 📚 Structured revision materials organized by level and units
- 🤖 AI-powered tutoring and explanations
- 📅 Smart study planner with exam countdown
- 📊 Progress tracking and weakness analysis
- 📝 Mock exams and practice questions
- 💳 Subscription-based monetization with M-Pesa integration

## 🏗️ Project Structure

```
cpa_smart_revision/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── config/                 # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/          # User authentication & management
│   ├── content/           # Levels, Units, Topics
│   ├── revision/          # Study materials & progress
│   ├── ai_tutor/          # AI integration
│   ├── planner/           # Study scheduling
│   ├── subscriptions/     # Payment & plans
│   └── analytics/         # Progress tracking
├── static/                # CSS, JS, images
├── media/                 # User uploads
└── templates/             # HTML templates
```

## 🎯 Features by Phase

### ✅ Phase 1-2 (Foundation & Core System)
- [x] Custom user model with student profiles
- [x] Multi-level content structure (Foundation, Intermediate, Advanced)
- [x] Topic organization (Part A/B, Units)
- [x] Student registration and authentication
- [x] Admin content management
- [x] Progress tracking
- [x] Search functionality

### 🔄 Phase 3-4 (Advanced Features)
- [ ] AI-powered explanations
- [ ] Mock question generator
- [ ] Study planner with calendar
- [ ] Usage limits per subscription tier

### 💰 Phase 5-6 (SaaS Features)
- [ ] M-Pesa Daraja API integration
- [ ] Subscription management
- [ ] Email verification
- [ ] Admin analytics dashboard

### 🚀 Phase 7 (Deployment)
- [ ] Production deployment
- [ ] SSL/HTTPS setup
- [ ] Performance optimization

## 💻 Technology Stack

**Backend:**
- Django 4.2+
- Django REST Framework
- PostgreSQL (Production) / SQLite (Development)
- Redis (Optional - AI caching)

**Frontend:**
- Django Templates
- Bootstrap 5
- Alpine.js (for interactivity)

**AI Integration:**
- OpenAI API / Anthropic Claude API
- Custom prompt engineering for CPA content

**Payments:**
- M-Pesa Daraja API (Primary)
- Stripe (International)
- Flutterwave (Alternative)

## 📦 Installation

### Prerequisites
- Python 3.10+
- pip
- virtualenv
- PostgreSQL (for production)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd cpa_smart_revision
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Database setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Load initial data (optional)**
```bash
python manage.py loaddata initial_data.json
```

8. **Run development server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000`

## 🔐 Environment Variables

Required variables in `.env`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=cpa_revision_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# AI API Keys
OPENAI_API_KEY=your-openai-key
# OR
ANTHROPIC_API_KEY=your-anthropic-key

# M-Pesa (Production)
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 💳 Subscription Plans

| Plan | Price (KES) | Features |
|------|-------------|----------|
| **Free** | 0 | Limited topics, 5 AI questions/month |
| **Basic** | 500/month | Full topic access, 50 AI questions/month |
| **Premium** | 1,200/month | Unlimited AI, planner, mock exams, analytics |
| **Annual** | 8,000/year | Premium features (33% discount) |
| **Institutional** | Custom | Bulk student accounts, admin dashboard |

## 🗄️ Database Models

### Core Models

**User (Custom)**
- Email-based authentication
- Student profile
- Subscription tier
- Registration date

**Level**
- Foundation / Intermediate / Advanced

**Part**
- Part A / Part B

**Unit**
- Belongs to Level and Part
- Unit code and name

**Topic**
- Belongs to Unit
- Content, examples, references

**Progress**
- Student + Topic
- Completion status
- Time spent

## 🤖 AI Integration

The AI tutor provides:
- Topic explanations in simple language
- Step-by-step problem solving
- Conceptual clarifications
- Mock question generation
- Summary creation

**Usage Limits by Plan:**
- Free: 5 requests/month
- Basic: 50 requests/month
- Premium: Unlimited

## 📊 Admin Features

Admins can:
- Upload and manage content
- Create units and topics
- View student analytics
- Manage subscriptions
- Control AI usage limits
- Export progress reports

## 🚀 Deployment

### Recommended Platforms
1. **Railway** - Easiest, auto-deployment
2. **Render** - Free tier available
3. **DigitalOcean** - Full control, affordable
4. **AWS/Azure** - Enterprise scale

### Deployment Checklist
- [ ] Set DEBUG=False
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Set up PostgreSQL database
- [ ] Configure static files (WhiteNoise/S3)
- [ ] Set up SSL certificate
- [ ] Configure email backend
- [ ] Set up M-Pesa webhook endpoints
- [ ] Enable security middleware
- [ ] Set up monitoring (Sentry)

## 📈 Marketing Strategy

1. **Campus Outreach**
   - Partner with CPA tuition centers
   - Campus ambassador program
   - Free trials for first 100 students

2. **Digital Marketing**
   - WhatsApp groups (CPA students)
   - Facebook groups
   - Instagram educational content
   - YouTube tutorials

3. **Content Marketing**
   - Free revision notes
   - Study tips blog
   - Telegram study bot

4. **Partnerships**
   - Universities offering CPA
   - Professional accounting bodies
   - Study groups

## ⚖️ Legal Compliance

**Important Notes:**
- Do not upload copyrighted KASNEB past papers without permission
- Create original study materials or use licensed content
- Ensure compliance with Kenya Data Protection Act
- Include proper Terms of Service and Privacy Policy
- Get business registration and KRA PIN

## 🔄 Future Roadmap (Version 2)

- Mobile app (React Native/Flutter)
- Support for ACCA, CIFA, CFE
- Live study groups
- Peer-to-peer tutoring marketplace
- Mock exam timer simulation
- AI exam predictor
- Gamification (badges, leaderboards)
- Offline mode

## 🤝 Contributing

This is a commercial project. If you're interested in contributing or partnering, please contact:

Email: [your-email]
Phone: [your-phone]

## 📄 License

Proprietary - All Rights Reserved

## 👨‍💻 Developer

Built by a CPA student and developer in Kenya.

**Why this works:**
- Domain expertise (CPA knowledge)
- Technical skills (Django development)
- Market understanding (Kenyan EdTech)

## 📞 Support

For support, email [support-email] or join our WhatsApp community.

---

**🎯 Vision:** Become the #1 CPA revision platform in East Africa, helping thousands of students pass their KASNEB exams.

**🚀 Mission:** Make quality CPA education accessible and affordable through technology.
