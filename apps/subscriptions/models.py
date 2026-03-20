"""
Subscription and payment models.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    """Subscription plans available."""

    PLAN_TYPES = [
        ("free", "Free"),
        ("basic", "Basic"),
        ("premium", "Premium"),
        ("institutional", "Institutional"),
    ]

    BILLING_PERIODS = [
        ("monthly", "Monthly"),
        ("annual", "Annual"),
        ("lifetime", "Lifetime"),
    ]

    name = models.CharField(max_length=50, unique=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    billing_period = models.CharField(max_length=20, choices=BILLING_PERIODS)

    price = models.DecimalField(max_digits=10, decimal_places=2)  # In KES
    currency = models.CharField(max_length=3, default="KES")

    # Features
    ai_questions_limit = models.IntegerField(
        help_text="AI questions per month (999999 = unlimited)"
    )
    can_access_premium_content = models.BooleanField(default=False)
    can_use_study_planner = models.BooleanField(default=True)
    can_take_mock_exams = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)

    # Ordering
    order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    description = models.TextField()
    features_list = models.TextField(help_text="One feature per line")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}/{self.billing_period}"


class Subscription(models.Model):
    """User subscription."""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
        ("pending", "Pending Payment"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)

    auto_renew = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return f"{self.user.email} - {self.plan.name} - {self.status}"

    def is_active(self):
        """Check if subscription is currently active."""
        return self.status == "active" and self.expires_at > timezone.now()

    def days_remaining(self):
        """Calculate days until expiration."""
        if self.expires_at > timezone.now():
            delta = self.expires_at - timezone.now()
            return delta.days
        return 0

    def activate(self):
        """Activate the subscription."""
        self.status = "active"

        # Set expiration based on billing period
        if self.plan.billing_period == "monthly":
            self.expires_at = timezone.now() + timedelta(days=30)
        elif self.plan.billing_period == "annual":
            self.expires_at = timezone.now() + timedelta(days=365)
        elif self.plan.billing_period == "lifetime":
            self.expires_at = timezone.now() + timedelta(days=36500)  # 100 years

        self.save()


class Payment(models.Model):
    """Payment transactions."""

    PAYMENT_METHODS = [
        ("mpesa", "M-Pesa"),
        ("stripe", "Stripe"),
        ("flutterwave", "Flutterwave"),
        ("manual", "Manual"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Payment gateway details
    transaction_id = models.CharField(max_length=200, unique=True)
    gateway_response = models.JSONField(null=True, blank=True)

    # M-Pesa specific
    mpesa_receipt_number = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency} - {self.status}"

    def mark_completed(self):
        """Mark payment as completed."""
        self.status = "completed"
        self.completed_at = timezone.now()
        self.save()

        # Activate subscription
        self.subscription.activate()


class AIUsage(models.Model):
    """Track AI feature usage for billing."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_usage"
    )

    month = models.DateField()  # First day of the month
    questions_asked = models.IntegerField(default=0)
    tokens_used = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "month"]
        verbose_name = "AI Usage"
        verbose_name_plural = "AI Usage Records"

    def __str__(self):
        return f"{self.user.email} - {self.month.strftime('%B %Y')} - {self.questions_asked} questions"

    def can_use_ai(self):
        """Check if user can use AI based on subscription plan or free limit."""
        from django.conf import settings
        try:
            subscription = self.user.subscription
            if subscription.is_active():
                limit = subscription.plan.ai_questions_limit
                return self.questions_asked < limit
        except Exception:
            pass
        
        # Default to free limit if no active subscription
        return self.questions_asked < settings.FREE_PLAN_AI_LIMIT

    def increment_usage(self, tokens=0):
        """Increment AI usage counters."""
        self.questions_asked += 1
        self.tokens_used += tokens
        self.save()
