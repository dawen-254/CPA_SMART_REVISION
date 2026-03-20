"""
Custom User model for CPA Smart Revision.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email as username."""

    username = None  # Remove username field
    email = models.EmailField(_("email address"), unique=True)

    # Student information
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    full_name = models.CharField(max_length=200)

    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Email verification
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name else self.email

    @property
    def is_enrolled(self):
        """Check if user is enrolled in any level/part."""
        return self.enrollments.filter(is_active=True).exists()


class StudentProfile(models.Model):
    """Extended profile for students."""

    LEVEL_CHOICES = [
        ("foundation", "Foundation"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    PART_CHOICES = [
        ("part_a", "Part A"),
        ("part_b", "Part B"),
        ("both", "Both Parts"),
    ]

    STUDY_TIME_CHOICES = [
        ("early_morning", "Early Morning (5-7 AM)"),
        ("morning", "Morning (7-10 AM)"),
        ("afternoon", "Afternoon (12-3 PM)"),
        ("evening", "Evening (3-6 PM)"),
        ("night", "Night (6-9 PM)"),
        ("late_night", "Late Night (9 PM+)"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )

    # Study information
    current_level = models.CharField(
        max_length=20, choices=LEVEL_CHOICES, default="foundation"
    )
    current_part = models.CharField(
        max_length=10, choices=PART_CHOICES, default="part_a"
    )
    exam_date = models.DateField(null=True, blank=True)

    # Profile details
    institution = models.CharField(max_length=200, blank=True, null=True)
    student_id = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # Study preferences
    daily_study_goal_minutes = models.IntegerField(default=120)  # 2 hours default
    preferred_study_time = models.CharField(
        max_length=20,
        choices=STUDY_TIME_CHOICES,
        default="morning"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

    def __str__(self):
        return f"{self.user.full_name} - {self.get_current_level_display()}"

    def get_subscription_plan(self):
        """Get current active subscription plan."""
        from apps.subscriptions.models import Subscription

        try:
            return self.user.subscription
        except Subscription.DoesNotExist:
            return None

    def days_until_exam(self):
        """Calculate days remaining until exam."""
        if not self.exam_date:
            return None
        from datetime import date

        delta = self.exam_date - date.today()
        return delta.days if delta.days > 0 else 0
