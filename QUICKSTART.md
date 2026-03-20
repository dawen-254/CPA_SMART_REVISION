# ⚡ QUICK START GUIDE - CPA Smart Revision

## 🎯 Get Running in 5 Minutes

### Step 1: Extract & Navigate
```bash
# Extract the zip file and navigate to the project
cd cpa_smart_revision
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment
```bash
# Copy the example env file
cp .env.example .env

# Generate a secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copy the output and paste it in .env as SECRET_KEY
```

### Step 5: Initialize Database
```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Enter: email, full name, password
```

### Step 6: Run the Server
```bash
python manage.py runserver
```

### Step 7: Access the Application
Open your browser and visit:
- **Homepage**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
  - Login with the superuser credentials you created

---

## 🎨 First Tasks

### 1. Add Subscription Plans
Visit admin panel → Subscriptions → Subscription Plans → Add

Create these plans:
- **Free**: Price 0, AI Limit 5
- **Basic**: Price 500, AI Limit 50
- **Premium**: Price 1200, AI Limit 999999

### 2. Add Content Structure
1. **Create Level**: Foundation/Intermediate/Advanced
2. **Create Part**: Part A/Part B
3. **Create Unit**: Financial Accounting, Taxation, etc.
4. **Create Topics**: Individual learning topics

### 3. Test User Registration
- Visit http://localhost:8000
- Click "Sign Up Free"
- Create a test student account
- Explore the interface

---

## 📁 Key Files to Know

- `config/settings.py` - Django configuration
- `config/urls.py` - URL routing
- `.env` - Environment variables (SECRET_KEY, etc.)
- `apps/accounts/models.py` - User models
- `apps/content/models.py` - Content structure
- `apps/subscriptions/models.py` - Subscription logic

---

## 🔧 Next Development Steps

See these files for detailed instructions:
1. **README.md** - Project overview
2. **SETUP_GUIDE.md** - Detailed setup & deployment
3. **DEVELOPMENT_ROADMAP.md** - What to build next
4. **PROJECT_SUMMARY.md** - Complete project status

---

## 🆘 Common Issues

**Issue**: `ModuleNotFoundError: No module named 'django'`
**Fix**: Make sure virtual environment is activated

**Issue**: Database errors
**Fix**: Delete `db.sqlite3` and run migrations again

**Issue**: Static files not loading
**Fix**: Run `python manage.py collectstatic`

---

## ✅ You're Ready!

The foundation is complete. Now you need to:
1. Implement view functions
2. Create forms
3. Add AI integration
4. Set up payments
5. Deploy!

**Check DEVELOPMENT_ROADMAP.md for the complete roadmap.**

Good luck! 🚀
