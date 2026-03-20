from datetime import date, timedelta
from django.db import transaction
from django.db.models import Avg, Count, Q, FloatField
from django.db.models.functions import Cast
from .models import StudyTask
from apps.content.models import Enrollment, Unit, Topic
from apps.revision.models import TopicProgress, QuestionAttempt

def rebalance_study_schedule(student):
    """
    Analyze student performance and add revision tasks for weak areas.
    'Dynamic Learning Paths' implementation.
    """
    # 1. Identify weak topics based on question attempts (accuracy < 60%)
    # Cast is_correct to FloatField so Avg returns a float, not a boolean/confused type
    weak_topic_ids = QuestionAttempt.objects.filter(
        student=student
    ).values('question__topic').annotate(
        accuracy=Avg(Cast('is_correct', FloatField()))
    ).filter(
        accuracy__lt=0.6
    ).values_list('question__topic_id', flat=True)

    # 2. Identify topics with low confidence level (1 or 2)
    low_confidence_topic_ids = TopicProgress.objects.filter(
        student=student,
        confidence_level__in=[1, 2] # 1: Weak, 2: Average
    ).values_list('topic_id', flat=True)

    # Combine weak areas
    all_weak_topic_ids = set(list(weak_topic_ids) + list(low_confidence_topic_ids))
    
    if not all_weak_topic_ids:
        return True, "No weak areas identified. Keep it up!"

    weak_topics = Topic.objects.filter(id__in=all_weak_topic_ids)
    
    with transaction.atomic():
        # Get next 7 available days for revision tasks
        start_date = date.today() + timedelta(days=1)
        
        # We'll insert revision tasks for these weak topics
        # alongside regular study tasks, but limited to 1 revision task per day
        for i, topic in enumerate(weak_topics):
            scheduled_date = start_date + timedelta(days=i)
            
            # Don't schedule past the exam date
            if student.student_profile.exam_date and scheduled_date >= student.student_profile.exam_date:
                break
                
            StudyTask.objects.get_or_create(
                student=student,
                topic=topic,
                scheduled_date=scheduled_date,
                task_type="revision", # Prioritize revision for weak areas
                defaults={'is_completed': False}
            )

    return True, f"Identified {len(all_weak_topic_ids)} weak topics and scheduled revision tasks."

def generate_study_schedule(student):
    """
    Automatically generate a study schedule based on enrolled units and exam date.
    """
    profile = student.student_profile
    if not profile.exam_date:
        return False, "Exam date not set."

    # Get active enrollments
    enrollments = Enrollment.objects.filter(student=student, is_active=True)
    if not enrollments.exists():
        return False, "No enrolled units found."

    # Get all units and their topics
    enrolled_units = []
    for enrollment in enrollments:
        enrolled_units.extend(enrollment.get_units())

    all_topics = Topic.objects.filter(
        unit__in=enrolled_units,
        is_published=True
    ).order_by('unit__order', 'order')

    if not all_topics.exists():
        return False, "No topics found for enrolled units."

    # Calculate days available
    start_date = date.today()
    end_date = profile.exam_date
    available_days = (end_date - start_date).days

    if available_days <= 0:
        return False, "Exam date must be in the future."

    # Reserve last 7 days for revision/practice if possible
    revision_period = min(7, available_days // 4)
    study_period = available_days - revision_period

    topics_list = list(all_topics)
    total_topics = len(topics_list)

    # Topics per day
    topics_per_day = max(1, total_topics // study_period)
    
    with transaction.atomic():
        # Clear existing uncompleted tasks
        StudyTask.objects.filter(student=student, is_completed=False).delete()

        current_date = start_date
        topic_index = 0

        # Assign study tasks
        while topic_index < total_topics and current_date < (end_date - timedelta(days=revision_period)):
            for _ in range(topics_per_day):
                if topic_index < total_topics:
                    StudyTask.objects.create(
                        student=student,
                        topic=topics_list[topic_index],
                        scheduled_date=current_date,
                        task_type="study"
                    )
                    topic_index += 1
            current_date += timedelta(days=1)

        # Assign remaining topics if any
        while topic_index < total_topics:
            StudyTask.objects.create(
                student=student,
                topic=topics_list[topic_index],
                scheduled_date=current_date,
                task_type="study"
            )
            topic_index += 1
            if topic_index < total_topics:
                # Add more to same day if we're running out of time
                if current_date < (end_date - timedelta(days=revision_period)):
                    current_date += timedelta(days=1)

        # Assign revision/practice tasks in the last few days
        # For simplicity, we'll just pick some key units or topics to revise
        # or just set practice tasks for the units
        current_date = end_date - timedelta(days=revision_period)
        while current_date < end_date:
            # Pick a unit to practice each day
            for unit in enrolled_units:
                if current_date < end_date:
                    # Just pick the first topic of the unit as a placeholder for practice
                    # In a real app, this might be a 'Unit Practice' task
                    first_topic = unit.topics.first()
                    if first_topic:
                        StudyTask.objects.get_or_create(
                            student=student,
                            topic=first_topic,
                            scheduled_date=current_date,
                            task_type="practice"
                        )
                    current_date += timedelta(days=1)
            if current_date < end_date:
                current_date += timedelta(days=1)

    return True, f"Successfully generated schedule with {total_topics} topics."
