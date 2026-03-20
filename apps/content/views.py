from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q
from .models import Unit, Level, Part, Enrollment, Topic


@login_required
def unit_list(request):
    """View to list all study units."""
    # Check if student is already enrolled
    existing_enrollment = Enrollment.objects.filter(
        student=request.user,
        is_active=True
    ).first()
    
    if existing_enrollment:
        messages.info(request, f"You are already enrolled in {existing_enrollment.level.get_name_display()} {existing_enrollment.part.get_name_display()}. You cannot enroll in another part.")
        return redirect('accounts:dashboard')
    
    levels = Level.objects.filter(is_active=True).prefetch_related('parts').order_by('order')
    
    context = {
        'levels': levels,
    }
    return render(request, 'content/unit_list.html', context)


@login_required
def level_detail(request, level_id, part_name):
    """Display units for a specific level and part with enrollment form."""
    level = get_object_or_404(Level, id=level_id, is_active=True)
    part = get_object_or_404(Part, level=level, name=part_name)
    
    # Check if student already has an active enrollment in a different part
    existing_enrollment = Enrollment.objects.filter(
        student=request.user,
        is_active=True
    ).first()
    
    if existing_enrollment and not (existing_enrollment.level_id == level.id and existing_enrollment.part_id == part.id):
        messages.warning(request, f"You are already enrolled in {existing_enrollment.level.get_name_display()} {existing_enrollment.part.get_name_display()}. You cannot enroll in another part.")
        return redirect('accounts:dashboard')
    
    units = Unit.objects.filter(level=level, part=part, is_active=True).order_by('order')
    
    enrollment = Enrollment.objects.filter(
        student=request.user,
        level=level,
        part=part
    ).first()
    
    is_enrolled = enrollment is not None and enrollment.is_active
    
    context = {
        'level': level,
        'part': part,
        'units': units,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
    }
    return render(request, 'levels/level_detail.html', context)


@login_required
def enroll(request, level_id, part_name):
    """Handle enrollment in a specific level and part."""
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    level = get_object_or_404(Level, id=level_id, is_active=True)
    part = get_object_or_404(Part, level=level, name=part_name)
    
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        level=level,
        part=part,
        defaults={'is_active': True}
    )
    
    if not created and not enrollment.is_active:
        enrollment.is_active = True
        enrollment.save()
    
    messages.success(request, f"Congratulations! You have successfully enrolled in {level.get_name_display()} {part.get_name_display()}.")
    return redirect('accounts:dashboard')


@login_required
def unenroll(request, enrollment_id):
    """Handle unenrollment from a level/part."""
    if request.method != 'POST':
        return HttpResponseForbidden()
    
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    level = enrollment.level
    part = enrollment.part
    
    enrollment.is_active = False
    enrollment.save()
    
    messages.success(request, f"Unenrolled from {level.get_name_display()} {part.get_name_display()}")
    return redirect('content:level_detail', level_id=level.id, part_name=part.name)


@login_required
def unit_detail(request, unit_slug):
    """Display a specific unit with its topics."""
    unit = get_object_or_404(Unit, slug=unit_slug, is_active=True)
    topics = unit.topics.filter(is_published=True).order_by('order')
    
    enrollment = Enrollment.objects.filter(
        student=request.user,
        level=unit.level,
        part=unit.part
    ).first()
    
    is_enrolled = enrollment is not None and enrollment.is_active
    
    from apps.revision.models import TopicProgress
    
    topics_data = []
    
    if unit.syllabus_file:
        topics_data.append({
            'topic': None,
            'is_completed': False,
            'is_syllabus': True,
            'syllabus_file': unit.syllabus_file,
            'unit_name': unit.name,
            'unit_code': unit.code
        })
    
    if is_enrolled:
        for topic in topics:
            progress = TopicProgress.objects.filter(
                student=request.user,
                topic=topic
            ).first()
            topics_data.append({
                'topic': topic,
                'is_completed': progress and progress.is_completed,
                'is_syllabus': False
            })
    else:
        for topic in topics:
            topics_data.append({
                'topic': topic,
                'is_completed': False,
                'is_syllabus': False
            })
    
    context = {
        'unit': unit,
        'topics': topics,
        'topics_data': topics_data,
        'is_enrolled': is_enrolled,
    }
    
    return render(request, 'content/unit_detail.html', context)


@login_required
def search_enrolled_content(request):
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    enrollments = Enrollment.objects.filter(
        student=request.user,
        is_active=True
    )
    
    if not enrollments.exists():
        return JsonResponse({'results': []})
    
    enrollment_filters = Q()
    for enrollment in enrollments:
        enrollment_filters |= Q(level=enrollment.level, part=enrollment.part)
    
    enrolled_units = Unit.objects.filter(
        enrollment_filters,
        is_active=True
    ).distinct()
    
    topics = Topic.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query),
        unit__in=enrolled_units,
        is_published=True
    ).select_related('unit')[:10]
    
    questions = request.user.question_attempts.filter(
        question__question_text__icontains=query,
        question__topic__unit__in=enrolled_units
    ).select_related('question__topic__unit').values(
        'question__id',
        'question__question_text',
        'question__topic__title',
        'question__topic__slug',
        'question__topic__unit__name',
        'question__topic__unit__slug'
    ).distinct()[:10]
    
    results = []
    
    for topic in topics:
        results.append({
            'type': 'topic',
            'title': topic.title,
            'unit': topic.unit.name,
            'unit_slug': topic.unit.slug,
            'topic_slug': topic.slug,
            'url': f'/content/unit/{topic.unit.slug}/#topic-{topic.slug}'
        })
    
    for question in questions:
        results.append({
            'type': 'question',
            'title': question['question__question_text'][:100],
            'unit': question['question__topic__unit__name'],
            'unit_slug': question['question__topic__unit__slug'],
            'topic_slug': question['question__topic__slug'],
            'url': f'/content/unit/{question["question__topic__unit__slug"]}/#topic-{question["question__topic__slug"]}'
        })
    
    return JsonResponse({'results': results})
