from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import User, StudentProfile
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Avg, Q



def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        current_level = request.POST.get("current_level", None)
        current_part = request.POST.get("current_part", None)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "register.html")

        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                full_name=full_name,
                phone_number=phone_number
            )
            # Update profile created by signal
            profile = user.student_profile
            if current_level:
                profile.current_level = current_level
            if current_part:
                profile.current_part = current_part
            profile.save()
            
            # Initialize UnitProgress for the selected level/part (only if provided)
            if current_level and current_part:
                from apps.content.models import Unit
                from apps.revision.models import UnitProgress
                
                parts_to_enroll = []
                if current_part == 'both':
                    parts_to_enroll = ['part_a', 'part_b']
                else:
                    parts_to_enroll = [current_part]
                    
                units = Unit.objects.filter(
                    level__name=current_level,
                    part__name__in=parts_to_enroll
                )
                
                for unit in units:
                    UnitProgress.objects.get_or_create(student=user, unit=unit)
                
                enrollment_message = f"Congratulations {full_name}! Your account has been created and you've been successfully enrolled in your units."
            else:
                enrollment_message = f"Congratulations {full_name}! Your account has been created. Please select your study units to get started."
            
            login(request, user)
            messages.success(request, enrollment_message)
            return redirect("accounts:dashboard")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, "register.html")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            
            messages.success(request, f"Welcome back, {user.full_name}!")
            return redirect("accounts:dashboard")
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, "login.html")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def profile_view(request):
    profile = request.user.student_profile
    context = {
        'profile': profile
    }
    return render(request, "accounts/profile.html", context)


@login_required
def edit_profile_view(request):
    from .forms import StudentProfileForm
    
    profile = request.user.student_profile
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('accounts:profile')
    else:
        form = StudentProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile
    }
    return render(request, "accounts/edit_profile.html", context)


@login_required
def units(request):
    return render(request, "content/units.html")


@login_required
def dashboard_view(request):
    from apps.revision.models import TopicProgress, StudySession, QuestionAttempt
    from apps.subscriptions.models import Subscription
    from apps.content.models import Unit, Enrollment
    
    user = request.user
    
    # Check if user has active subscription OR is enrolled
    # If not, redirect to pricing
    has_active_sub = False
    try:
        has_active_sub = user.subscription.is_active()
    except Subscription.DoesNotExist:
        pass
        
    if not has_active_sub and not user.is_enrolled:
        messages.info(request, "Please choose a subscription plan or enroll in a unit to access your dashboard.")
        return redirect('subscriptions:plans')

    today = timezone.now().date()
    
    # Get user's topic progress
    topic_progress = TopicProgress.objects.filter(student=user).select_related('topic')
    topics_completed = topic_progress.filter(is_completed=True).count()
    
    # Get questions answered
    questions_answered = QuestionAttempt.objects.filter(student=user).count()
    
    # Calculate accuracy rate
    correct_attempts = QuestionAttempt.objects.filter(
        student=user,
        is_correct=True
    ).count()
    accuracy_rate = (correct_attempts / questions_answered * 100) if questions_answered > 0 else 0
    
    # Get days until exam from student profile
    profile = user.student_profile
    days_until_exam = profile.days_until_exam() if profile.exam_date else None
    
    # Get study sessions for recent activity
    study_sessions = StudySession.objects.filter(student=user)
    
    # Calculate study streak from most recent session backwards
    study_streak = 0
    latest_session = study_sessions.order_by('-started_at').first()
    
    if latest_session:
        current_date = latest_session.started_at.date()
        while True:
            if StudySession.objects.filter(
                student=user,
                started_at__date=current_date
            ).exists():
                study_streak += 1
                current_date -= timedelta(days=1)
            else:
                break
    
    # Get recent study sessions
    recent_sessions = study_sessions.order_by('-started_at')[:5]
    
    # Get user's enrollments
    enrollments = Enrollment.objects.filter(
        student=user,
        is_active=True
    ).select_related('level', 'part').prefetch_related('part__units')
    
    # Get unit progress (aggregated) - only for enrolled units
    enrolled_unit_ids = []
    enrolled_units_data = []
    
    for enrollment in enrollments:
        enrollment.units_list = enrollment.get_units()
        for unit in enrollment.units_list:
            enrolled_unit_ids.append(unit.id)
            unit_topics = unit.topics.filter(is_published=True)
            total_topics = unit_topics.count()
            completed_topics = TopicProgress.objects.filter(
                student=user,
                topic__in=unit_topics,
                is_completed=True
            ).count()
            
            completion_percentage = (completed_topics / total_topics * 100) if total_topics > 0 else 0
            
            enrolled_units_data.append({
                'unit': unit,
                'completion_percentage': int(completion_percentage),
                'completed_topics': completed_topics,
                'total_topics': total_topics,
                'enrollment': enrollment
            })
    
    unit_progress_data = []
    if enrolled_unit_ids:
        units = Unit.objects.filter(id__in=enrolled_unit_ids)
        for unit in units:
            unit_topics = unit.topics.all()
            total_topics = unit_topics.count()
            completed_topics = TopicProgress.objects.filter(
                student=user,
                topic__in=unit_topics,
                is_completed=True
            ).count()
            
            if total_topics > 0:
                completion_percentage = (completed_topics / total_topics) * 100
                unit_progress_data.append({
                    'name': unit.name,
                    'code': unit.code,
                    'completion_percentage': int(completion_percentage),
                    'completed_topics': completed_topics,
                    'total_topics': total_topics
                })
    
    # Get subscription info
    try:
        subscription = user.subscription
    except Exception:
        subscription = None
    
    # Get today's study tasks
    from apps.planner.models import StudyTask
    from apps.planner.services import rebalance_study_schedule
    
    # Proactively rebalance the schedule for the student if needed
    # We can do this once a day or on a button click, but for now we'll do it on dashboard view
    try:
        rebalance_study_schedule(user)
    except Exception as e:
        # Don't let schedule errors crash the dashboard
        import logging
        logging.getLogger(__name__).error(f"Schedule rebalance error: {str(e)}")
    
    today_tasks = StudyTask.objects.filter(
        student=user,
        scheduled_date=today
    )
    
    context = {
        'today': today,
        'topics_completed': topics_completed,
        'questions_answered': questions_answered,
        'days_until_exam': days_until_exam,
        'accuracy_rate': int(accuracy_rate),
        'study_streak': study_streak,
        'recent_sessions': recent_sessions,
        'unit_progress': unit_progress_data,
        'enrollments': enrollments,
        'enrolled_units': enrolled_units_data,
        'subscription': subscription,
        'today_tasks': today_tasks,
    }
    
    return render(request, "dashboard.html", context)



