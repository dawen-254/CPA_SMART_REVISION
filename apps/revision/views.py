from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import TopicProgress, StudySession, UnitProgress, Flashcard, FlashcardProgress
from .services import FlashcardService

@login_required
def generate_flashcards_view(request, topic_id):
    """View to trigger AI generation of flashcards for a topic."""
    topic = get_object_or_404(Topic, id=topic_id)
    
    # Check if flashcards already exist to avoid duplicates
    if topic.flashcards.exists():
        messages.info(request, "Flashcards already exist for this topic.")
        return redirect('revision:flashcard_study', topic_id=topic.id)
        
    created_count, error = FlashcardService.generate_for_topic(topic.id)
    
    if error:
        messages.error(request, f"Failed to generate flashcards: {error}")
    else:
        messages.success(request, f"Successfully generated {created_count} flashcards for this topic!")
        
    return redirect('revision:flashcard_study', topic_id=topic.id)

@login_required
def flashcard_study_view(request, topic_id):
    """View to study flashcards for a specific topic."""
    topic = get_object_or_404(Topic, id=topic_id)
    flashcards = topic.flashcards.all()
    
    if not flashcards.exists():
        context = {
            'topic': topic,
            'no_flashcards': True
        }
        return render(request, 'revision/flashcards.html', context)
        
    # Get progress for all cards in this topic for this student
    # We'll use a simple approach: show cards that are due for review
    due_cards = []
    for card in flashcards:
        progress, _ = FlashcardProgress.objects.get_or_create(
            student=request.user,
            flashcard=card
        )
        if progress.next_review <= timezone.now():
            due_cards.append(card)
            
    # If no cards are due, we can still allow studying all of them
    study_cards = due_cards if due_cards else list(flashcards)
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle spaced repetition update
        card_id = request.POST.get('card_id')
        quality = int(request.POST.get('quality', 3)) # 0-5
        
        progress = get_object_or_404(FlashcardProgress, student=request.user, flashcard_id=card_id)
        progress.update_spaced_repetition(quality)
        
        return JsonResponse({
            'success': True,
            'next_review': progress.next_review.strftime('%Y-%m-%d'),
            'interval': progress.interval_days
        })

    context = {
        'topic': topic,
        'flashcards': study_cards,
        'total_count': flashcards.count(),
        'due_count': len(due_cards)
    }
    return render(request, 'revision/flashcards.html', context)
from apps.content.models import Topic


@login_required
def dashboard(request):
    user = request.user
    
    topic_progress = TopicProgress.objects.filter(student=user).select_related('topic')
    unit_progress = UnitProgress.objects.filter(student=user).select_related('unit')
    recent_sessions = StudySession.objects.filter(student=user).order_by('-started_at')[:10]
    
    context = {
        'topic_progress': topic_progress,
        'unit_progress': unit_progress,
        'recent_sessions': recent_sessions,
    }
    
    return render(request, 'revision/dashboard.html', context)


@login_required
def topic_detail(request, topic_slug):
    """Display a specific topic with content and progress tracking."""
    topic = get_object_or_404(Topic, slug=topic_slug, is_published=True)
    
    topic_progress, created = TopicProgress.objects.get_or_create(
        student=request.user,
        topic=topic
    )
    
    # Create study session for today if it doesn't exist
    from django.utils.timezone import now
    from datetime import datetime
    today = timezone.now().date()
    
    existing_session = StudySession.objects.filter(
        student=request.user,
        started_at__date=today
    ).first()
    
    if not existing_session:
        study_session = StudySession.objects.create(
            student=request.user,
            topic=topic,
            unit=topic.unit,
            started_at=now()
        )
    else:
        study_session = existing_session
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'mark_complete':
            if not topic_progress.is_completed:
                topic_progress.is_completed = True
                topic_progress.completion_date = timezone.now()
                topic_progress.save()
                
                unit_progress, _ = UnitProgress.objects.get_or_create(
                    student=request.user,
                    unit=topic.unit
                )
                unit_progress.update_progress()
                
                messages.success(request, f'Great! You\'ve completed "{topic.title}"')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'is_completed': topic_progress.is_completed,
                    'completion_date': topic_progress.completion_date.strftime('%B %d, %Y') if topic_progress.completion_date else None
                })
            else:
                return redirect('revision:topic_detail', topic_slug=topic_slug)
    
    topic_progress.views_count += 1
    topic_progress.save()
    
    next_topic = topic.get_next_topic()
    previous_topic = topic.get_previous_topic()
    
    context = {
        'topic': topic,
        'progress': topic_progress,
        'next_topic': next_topic,
        'previous_topic': previous_topic,
        'unit': topic.unit,
    }
    
    return render(request, 'revision/topic_detail.html', context)