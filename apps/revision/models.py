"""
Revision and progress tracking models.
"""
from django.db import models
from django.conf import settings
from apps.content.models import Topic, Unit, Question


class TopicProgress(models.Model):
    """Track student progress on individual topics."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="topic_progress",
    )
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name="student_progress"
    )

    # Progress tracking
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.IntegerField(default=0)

    # Engagement metrics
    views_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(auto_now=True)
    first_viewed = models.DateTimeField(auto_now_add=True)

    # Notes
    personal_notes = models.TextField(blank=True)
    bookmarked = models.BooleanField(default=False)

    # Confidence level
    confidence_level = models.IntegerField(
        default=0,
        choices=[
            (0, "Not Started"),
            (1, "Weak"),
            (2, "Average"),
            (3, "Good"),
            (4, "Excellent"),
        ],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["student", "topic"]
        verbose_name = "Topic Progress"
        verbose_name_plural = "Topic Progress"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.student.email} - {self.topic.title}"

    def mark_complete(self):
        """Mark topic as completed."""
        from django.utils import timezone

        self.is_completed = True
        self.completion_date = timezone.now()
        self.save()


class UnitProgress(models.Model):
    """Aggregate progress tracking for units."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="unit_progress"
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name="student_progress"
    )

    completion_percentage = models.IntegerField(default=0)
    total_time_spent_minutes = models.IntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["student", "unit"]
        verbose_name = "Unit Progress"
        verbose_name_plural = "Unit Progress"

    def __str__(self):
        return (
            f"{self.student.email} - {self.unit.name} ({self.completion_percentage}%)"
        )

    def update_progress(self):
        """Recalculate completion percentage based on topic progress."""
        total_topics = self.unit.topics.count()
        if total_topics == 0:
            self.completion_percentage = 0
        else:
            completed = TopicProgress.objects.filter(
                student=self.student, topic__unit=self.unit, is_completed=True
            ).count()
            self.completion_percentage = int((completed / total_topics) * 100)

        # Update total time spent
        self.total_time_spent_minutes = (
            TopicProgress.objects.filter(
                student=self.student, topic__unit=self.unit
            ).aggregate(models.Sum("time_spent_minutes"))["time_spent_minutes__sum"]
            or 0
        )

        self.save()


class QuestionAttempt(models.Model):
    """Track student attempts on practice questions."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="question_attempts",
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="attempts"
    )

    student_answer = models.CharField(max_length=500)
    is_correct = models.BooleanField()
    time_taken_seconds = models.IntegerField(default=0)

    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Question Attempt"
        verbose_name_plural = "Question Attempts"
        ordering = ["-attempted_at"]

    def __str__(self):
        return f"{self.student.email} - Q{self.question.id} - {'✓' if self.is_correct else '✗'}"


class StudySession(models.Model):
    """Track individual study sessions."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_sessions",
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)

    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Study Session"
        verbose_name_plural = "Study Sessions"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student.email} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"

from django.utils import timezone
from datetime import timedelta

class Flashcard(models.Model):
    """Flashcards generated for topics."""
    topic = models.ForeignKey(
        Topic, 
        on_delete=models.CASCADE, 
        related_name="flashcards"
    )
    front = models.TextField(help_text="Question or term")
    back = models.TextField(help_text="Answer or definition")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Flashcard"
        verbose_name_plural = "Flashcards"

    def __str__(self):
        return f"{self.topic.title} - {self.front[:50]}"

class FlashcardProgress(models.Model):
    """Track student progress on individual flashcards using Spaced Repetition (SM-2)."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="flashcard_progress"
    )
    flashcard = models.ForeignKey(
        Flashcard, 
        on_delete=models.CASCADE, 
        related_name="student_progress"
    )
    
    # SM-2 Algorithm fields
    easiness_factor = models.FloatField(default=2.5)
    interval_days = models.IntegerField(default=0)
    repetition_count = models.IntegerField(default=0)
    
    next_review = models.DateTimeField(default=timezone.now)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ["student", "flashcard"]
        verbose_name = "Flashcard Progress"
        verbose_name_plural = "Flashcard Progress"

    def __str__(self):
        return f"{self.student.email} - {self.flashcard.front[:30]}"
    
    def update_spaced_repetition(self, quality):
        """
        Update the flashcard progress using a simplified SM-2 algorithm.
        quality: 0-5 (0: complete blackout, 5: perfect response)
        """
        if quality >= 3:
            if self.repetition_count == 0:
                self.interval_days = 1
            elif self.repetition_count == 1:
                self.interval_days = 6
            else:
                self.interval_days = round(self.interval_days * self.easiness_factor)
            
            self.repetition_count += 1
        else:
            self.repetition_count = 0
            self.interval_days = 1
            
        self.easiness_factor = max(
            1.3, 
            self.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        )
        
        self.last_reviewed = timezone.now()
        self.next_review = self.last_reviewed + timedelta(days=self.interval_days)
        self.save()
