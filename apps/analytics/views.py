from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from apps.revision.models import TopicProgress, QuestionAttempt, StudySession
from apps.content.models import Enrollment, Unit, Topic

@login_required
def analytics_dashboard(request):
    user = request.user
    
    # Overall statistics
    total_topics_completed = TopicProgress.objects.filter(student=user, is_completed=True).count()
    total_questions_attempted = QuestionAttempt.objects.filter(student=user).count()
    correct_attempts = QuestionAttempt.objects.filter(student=user, is_correct=True).count()
    overall_accuracy = (correct_attempts / total_questions_attempted * 100) if total_questions_attempted > 0 else 0
    
    total_study_time = StudySession.objects.filter(student=user).aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
    
    # Progress by Unit
    unit_progress = []
    enrollments = Enrollment.objects.filter(student=user, is_active=True)
    for enrollment in enrollments:
        units = enrollment.get_units()
        for unit in units:
            topics = Topic.objects.filter(unit=unit, is_published=True)
            total_unit_topics = topics.count()
            completed_unit_topics = TopicProgress.objects.filter(
                student=user, 
                topic__unit=unit, 
                is_completed=True
            ).count()
            
            percentage = (completed_unit_topics / total_unit_topics * 100) if total_unit_topics > 0 else 0
            
            # Accuracy per unit
            unit_questions = QuestionAttempt.objects.filter(student=user, question__topic__unit=unit)
            unit_total = unit_questions.count()
            unit_correct = unit_questions.filter(is_correct=True).count()
            unit_accuracy = (unit_correct / unit_total * 100) if unit_total > 0 else 0
            
            unit_progress.append({
                'unit': unit,
                'percentage': int(percentage),
                'completed': completed_unit_topics,
                'total': total_unit_topics,
                'accuracy': int(unit_accuracy)
            })

    # Weekly study time (last 7 days)
    today = timezone.now().date()
    last_7_days = []
    study_time_data = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        last_7_days.append(day.strftime('%a'))
        daily_time = StudySession.objects.filter(
            student=user, 
            started_at__date=day
        ).aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
        study_time_data.append(daily_time)

    # Performance by topic confidence
    confidence_stats = TopicProgress.objects.filter(student=user).values('confidence_level').annotate(count=Count('id'))
    confidence_data = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for stat in confidence_stats:
        confidence_data[stat['confidence_level']] = stat['count']
    
    context = {
        'total_topics_completed': total_topics_completed,
        'total_questions_attempted': total_questions_attempted,
        'overall_accuracy': int(overall_accuracy),
        'total_study_time': total_study_time,
        'unit_progress': unit_progress,
        'last_7_days': last_7_days,
        'study_time_data': study_time_data,
        'confidence_data': list(confidence_data.values()),
    }
    
    return render(request, "analytics/dashboard.html", context)
