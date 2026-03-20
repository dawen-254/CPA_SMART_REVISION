"""
Signals for accounts app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, StudentProfile


@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    """Automatically create a StudentProfile when a User is created."""
    if created and not instance.is_superuser:
        StudentProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    """Save the StudentProfile when User is saved."""
    if not instance.is_superuser and hasattr(instance, "student_profile"):
        instance.student_profile.save()
