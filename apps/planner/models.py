from django.db import models
from django.conf import settings
from apps.content.models import Topic

class StudyTask(models.Model):
    """A single study task for a student."""
    TASK_TYPE_CHOICES = [
        ("study", "Initial Study"),
        ("revision", "Revision"),
        ("practice", "Practice Questions"),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_tasks"
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name="study_tasks"
    )
    scheduled_date = models.DateField()
    task_type = models.CharField(
        max_length=20,
        choices=TASK_TYPE_CHOICES,
        default="study"
    )
    is_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Study Task"
        verbose_name_plural = "Study Tasks"
        ordering = ["scheduled_date", "topic__order"]
        unique_together = ["student", "topic", "task_type", "scheduled_date"]

    def __str__(self):
        return f"{self.student.full_name} - {self.topic.title} ({self.get_task_type_display()})"
