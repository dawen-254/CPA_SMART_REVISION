from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .services import generate_study_schedule
from .models import StudyTask
from datetime import date, timedelta
import calendar

@login_required
def planner_dashboard(request):
    """View to show the Study Planner dashboard."""
    user = request.user
    profile = user.student_profile

    if not profile.exam_date:
        return render(request, "planner/exam_date_setup.html")

    # Get tasks for current month
    today = timezone.now().date()
    # Handle month navigation
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    tasks = StudyTask.objects.filter(
        student=user,
        scheduled_date__year=year,
        scheduled_date__month=month
    )
    
    # Calculate previous and next months
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    # Create calendar matrix
    cal = calendar.Calendar(firstweekday=6) # Sunday start
    month_days = cal.monthdays2calendar(year, month) # Returns list of weeks, each week is list of (day, weekday)
    
    # Enrich calendar days with tasks
    enriched_calendar = []
    for week in month_days:
        enriched_week = []
        for day, weekday in week:
            if day == 0:
                enriched_week.append({'day': 0, 'tasks': []})
            else:
                day_tasks = tasks.filter(scheduled_date__day=day)
                enriched_week.append({
                    'day': day,
                    'is_today': (day == today.day and month == today.month and year == today.year),
                    'tasks': day_tasks
                })
        enriched_calendar.append(enriched_week)

    context = {
        'profile': profile,
        'calendar': enriched_calendar,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': today,
    }
    return render(request, "planner/dashboard.html", context)

@login_required
def set_exam_date(request):
    """View to set or update the exam date and generate a schedule."""
    if request.method == "POST":
        exam_date_str = request.POST.get("exam_date")
        if exam_date_str:
            try:
                exam_date = timezone.datetime.strptime(exam_date_str, "%Y-%m-%d").date()
                if exam_date <= timezone.now().date():
                    messages.error(request, "Exam date must be in the future.")
                    return redirect("planner:dashboard")
                
                profile = request.user.student_profile
                profile.exam_date = exam_date
                profile.save()
                
                success, message = generate_study_schedule(request.user)
                if success:
                    messages.success(request, f"Exam date set to {exam_date}. {message}")
                else:
                    messages.warning(request, f"Exam date set, but schedule generation failed: {message}")
                
                return redirect("planner:dashboard")
            except ValueError:
                messages.error(request, "Invalid date format.")
        else:
            messages.error(request, "Please select an exam date.")
            
    return redirect("planner:dashboard")

@login_required
def regenerate_schedule(request):
    """View to manually regenerate the study schedule."""
    success, message = generate_study_schedule(request.user)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect("planner:dashboard")

@login_required
def toggle_task(request, task_id):
    """Toggle task completion status."""
    try:
        task = StudyTask.objects.get(id=task_id, student=request.user)
        task.is_completed = not task.is_completed
        task.save()
        
        # If completed, update topic progress
        if task.is_completed:
            from apps.revision.models import TopicProgress
            progress, created = TopicProgress.objects.get_or_create(
                student=request.user,
                topic=task.topic
            )
            progress.mark_complete()
            
        return redirect("planner:dashboard")
    except StudyTask.DoesNotExist:
        messages.error(request, "Task not found.")
        return redirect("planner:dashboard")
