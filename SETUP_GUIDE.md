# 🚀 CPA Smart Revision - Setup & Deployment Guide

## Quick Start (Development)

### 1. Prerequisites
```bash
# Check Python version (3.10+ required)
python3 --version

# Check pip
pip3 --version

# Install virtualenv if not installed
pip3 install virtualenv
```

### 2. Environment Setup

```bash
# Clone or navigate to project
cd cpa_smart_revision

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor

# Minimum required for development:
SECRET_KEY=your-generated-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. Generate Secret Key

```python
# Run in Python shell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copy the output to SECRET_KEY in .env
```

### 5. Database Setup

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Enter email, full name, and password
```

### 6. Load Initial Data (Optional)

```bash
# Create initial subscription plans
python manage.py shell

# Then run:
from apps.subscriptions.models import SubscriptionPlan

# Free Plan
SubscriptionPlan.objects.create(
    name="Free Plan",
    plan_type="free",
    billing_period="monthly",
    price=0,
    ai_questions_limit=5,
    can_access_premium_content=False,
    can_use_study_planner=True,
    can_take_mock_exams=False,
    can_view_analytics=False,
    description="Get started with basic features",
    features_list="Access to basic topics\n5 AI questions per month\nStudy planner\nProgress tracking",
    order=1
)

# Basic Plan
SubscriptionPlan.objects.create(
    name="Basic Plan",
    plan_type="basic",
    billing_period="monthly",
    price=500,
    ai_questions_limit=50,
    can_access_premium_content=False,
    can_use_study_planner=True,
    can_take_mock_exams=True,
    can_view_analytics=False,
    description="Full topic access for serious students",
    features_list="All topics access\n50 AI questions per month\nStudy planner\nMock exams\nProgress tracking",
    order=2
)

# Premium Plan
SubscriptionPlan.objects.create(
    name="Premium Plan",
    plan_type="premium",
    billing_period="monthly",
    price=1200,
    ai_questions_limit=999999,
    can_access_premium_content=True,
    can_use_study_planner=True,
    can_take_mock_exams=True,
    can_view_analytics=True,
    description="Unlimited access to all features",
    features_list="All premium topics\nUnlimited AI questions\nAdvanced study planner\nUnlimited mock exams\nDetailed analytics\nPriority support",
    order=3
)

# Premium Annual
SubscriptionPlan.objects.create(
    name="Premium Annual",
    plan_type="premium",
    billing_period="annual",
    price=8000,
    ai_questions_limit=999999,
    can_access_premium_content=True,
    can_use_study_planner=True,
    can_take_mock_exams=True,
    can_view_analytics=True,
    description="Best value - Save 33% with annual plan",
    features_list="All premium features\n33% discount\nPriority support\nOffline access (coming soon)",
    order=4
)
```

### 7. Create Sample Content (Optional)

```python
# Still in Django shell
from apps.content.models import Level, Part, Unit, Topic

# Create Foundation Level
foundation = Level.objects.create(
    name='foundation',
    code='F',
    description='CPA Foundation Level - Entry point for CPA qualification',
    order=1
)

# Create Parts
part_a = Part.objects.create(
    level=foundation,
    name='part_a',
    description='Foundation Part A subjects',
    order=1
)

# Create a sample unit
financial_accounting = Unit.objects.create(
    level=foundation,
    part=part_a,
    code='FAC',
    name='Financial Accounting',
    description='Introduction to financial accounting principles and practices',
    estimated_hours=40,
    difficulty_level='beginner',
    order=1
)

# Create a sample topic
Topic.objects.create(
    unit=financial_accounting,
    title='Introduction to Accounting',
    content='''# Introduction to Accounting

Accounting is the systematic recording, reporting, and analysis of financial transactions.

## Key Concepts:
- Double-entry bookkeeping
- Assets, Liabilities, and Equity
- The accounting equation: Assets = Liabilities + Equity

## Learning Objectives:
- Understand the basic principles of accounting
- Learn the accounting equation
- Recognize different types of accounts
''',
    summary='Learn the fundamental principles of accounting',
    objectives='Understand basic accounting concepts and the accounting equation',
    estimated_minutes=30,
    difficulty='easy',
    order=1,
    is_published=True
)
```

### 8. Run Development Server

```bash
# Collect static files (if needed)
python manage.py collectstatic --noinput

# Run development server
python manage.py runserver

# Visit http://localhost:8000
# Admin panel: http://localhost:8000/admin
```

## 📊 Admin Panel Usage

### Accessing Admin
1. Navigate to `http://localhost:8000/admin`
2. Login with superuser credentials
3. You'll see all models organized by app

### Adding Content Workflow
1. **Create Levels** (if not exists)
   - Foundation, Intermediate, Advanced

2. **Create Parts** for each level
   - Part A, Part B

3. **Create Units**
   - Select level and part
   - Add code (e.g., FAC, TAX)
   - Add description and estimated hours

4. **Create Topics**
   - Select parent unit
   - Write content in Markdown
   - Set difficulty and time estimates
   - Mark as published

5. **Add Questions** (optional)
   - Attach to topics
   - Create MCQs or other question types

## 🔐 API Setup (Optional)

### Get JWT Token
```bash
# Using curl
curl -X POST http://localhost:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}'

# Response will include access and refresh tokens
```

### Use Token for API Requests
```bash
curl http://localhost:8000/api/content/units/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 💳 M-Pesa Integration (Production)

### 1. Register for Daraja API
1. Visit https://developer.safaricom.co.ke
2. Create an account
3. Create an app
4. Get Consumer Key and Consumer Secret

### 2. Configure .env
```env
MPESA_ENVIRONMENT=sandbox  # or production
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_SHORTCODE=174379  # Your paybill/till
MPESA_PASSKEY=your_passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback/
```

### 3. Test in Sandbox
- Use test phone number: 254708374149
- Follow Safaricom's sandbox testing guide

## 🚀 Production Deployment

### Option 1: Railway (Recommended for Beginners)

```bash
# Install Railway CLI
npm install -g railway

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Add environment variables in Railway dashboard
```

### Option 2: DigitalOcean App Platform

1. Create DigitalOcean account
2. Create new App
3. Connect GitHub repo
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `gunicorn config.wsgi:application`
5. Add environment variables
6. Deploy

### Option 3: VPS (Ubuntu Server)

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install python3-pip python3-venv nginx postgresql -y

# Create application user
adduser cpaapp
su - cpaapp

# Clone repository
git clone your-repo.git
cd cpa_smart_revision

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt gunicorn

# Configure PostgreSQL
# ... (create database and user)

# Setup .env for production
nano .env
# Set DEBUG=False
# Set proper ALLOWED_HOSTS
# Configure database

# Run migrations
python manage.py migrate
python manage.py collectstatic

# Configure gunicorn service
# Configure nginx
# Setup SSL with Let's Encrypt
```

## 🔒 Security Checklist (Production)

- [ ] Change SECRET_KEY to a strong random value
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Set up database backups
- [ ] Configure email backend
- [ ] Enable Django security middleware
- [ ] Set up monitoring (Sentry)
- [ ] Configure rate limiting
- [ ] Review file upload settings

## 📧 Email Configuration

### Gmail Setup
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Not your Gmail password!
```

### Get Gmail App Password
1. Enable 2-factor authentication on Gmail
2. Go to Google Account > Security > App Passwords
3. Generate new app password
4. Use this in EMAIL_HOST_PASSWORD

## 🐛 Troubleshooting

### Issue: Import errors
**Solution**: Ensure virtual environment is activated

### Issue: Database errors
**Solution**: Run `python manage.py migrate`

### Issue: Static files not loading
**Solution**: Run `python manage.py collectstatic`

### Issue: M-Pesa callback not working
**Solution**: 
- Ensure callback URL is publicly accessible
- Use ngrok for local testing: `ngrok http 8000`
- Update MPESA_CALLBACK_URL with ngrok URL

## 📚 Next Steps

1. **Content Creation**: Start adding CPA revision materials
2. **AI Integration**: Configure OpenAI or Anthropic API
3. **Payment Testing**: Test M-Pesa integration in sandbox
4. **Marketing**: Set up social media and marketing materials
5. **Beta Testing**: Invite first users for feedback

## 🆘 Support

For issues or questions:
- Check Django logs: `python manage.py runserver` output
- Check production logs: `tail -f /var/log/gunicorn/error.log`
- Django debug toolbar for development
- Use `python manage.py shell` for debugging

## 📖 Useful Commands

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Check for issues
python manage.py check

# Open Django shell
python manage.py shell

# Database shell
python manage.py dbshell

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver 0.0.0.0:8000
```
