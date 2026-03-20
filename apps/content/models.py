"""
Content models for CPA revision materials.
Hierarchical structure: Level > Part > Unit > Topic
"""
from django.db import models
from django.utils.text import slugify


class Level(models.Model):
    """CPA Examination Level (Foundation, Intermediate, Advanced)."""

    LEVEL_CHOICES = [
        ("foundation", "Foundation"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    name = models.CharField(max_length=20, choices=LEVEL_CHOICES, unique=True)
    code = models.CharField(max_length=10, unique=True)  # e.g., "F", "I", "A"
    description = models.TextField()
    order = models.IntegerField(default=1) # For ordering levels (Foundation first, then Intermediate, etc.)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Level"
        verbose_name_plural = "Levels"

    def __str__(self):
        return self.get_name_display()

    def get_total_units(self):
        """Get total number of units in this level."""
        return self.units.count()


class Part(models.Model):
    """CPA Part (Part A or Part B)."""

    PART_CHOICES = [
        ("part_a", "Part A"),
        ("part_b", "Part B"),
    ]

    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="parts")
    name = models.CharField(max_length=10, choices=PART_CHOICES)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["level", "order"]
        unique_together = ["level", "name"]
        verbose_name = "Part"
        verbose_name_plural = "Parts"

    def __str__(self):
        return f"{self.level} - {self.get_name_display()}"

    def get_total_units(self):
        """Get total number of units in this part."""
        return self.units.count()


class Unit(models.Model):
    """CPA Study Unit (e.g., Financial Accounting, Taxation)."""

    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="units")
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name="units")

    code = models.CharField(max_length=20, unique=True)  # e.g., "FAC", "TAX"
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    

    # Unit metadata
    estimated_hours = models.IntegerField(default=40, help_text="Estimated study hours")
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        default="intermediate",
    )

    # Ordering
    order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    # Optional materials
    syllabus_file = models.FileField(upload_to="syllabi/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="unit_thumbnails/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["level", "part", "order"]
        unique_together = ["level", "part", "code"]
        verbose_name = "Unit"
        verbose_name_plural = "Units"

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.code}-{self.name}")
        super().save(*args, **kwargs)

    def get_total_topics(self):
        """Get total number of topics in this unit."""
        return self.topics.count()

    def get_completion_rate(self, user):
        """Calculate completion rate for a specific user."""
        from apps.revision.models import TopicProgress

        total_topics = self.get_total_topics()
        if total_topics == 0:
            return 0
        completed = TopicProgress.objects.filter(
            student=user, topic__unit=self, is_completed=True
        ).count()
        return int((completed / total_topics) * 100)


class Topic(models.Model):
    """Individual topic within a unit."""

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="topics")

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=350, unique=True, blank=True)

    # Content
    content = models.TextField(help_text="Main topic content in Markdown format")
    summary = models.TextField(blank=True, help_text="Brief summary of the topic")

    # Learning objectives
    objectives = models.TextField(blank=True, help_text="What students should learn")

    # Additional resources
    examples = models.TextField(blank=True, help_text="Practical examples")
    formulas = models.TextField(blank=True, help_text="Important formulas")
    references = models.TextField(
        blank=True, help_text="External references or citations"
    )

    # Metadata
    estimated_minutes = models.IntegerField(
        default=30, help_text="Estimated reading time"
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("easy", "Easy"),
            ("medium", "Medium"),
            ("hard", "Hard"),
        ],
        default="medium",
    )

    # Ordering and status
    order = models.IntegerField(default=1)
    is_published = models.BooleanField(default=True)
    is_premium = models.BooleanField(
        default=False, help_text="Requires premium subscription"
    )

    # Attachments
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or Vimeo URL")
    pdf_file = models.FileField(upload_to="topic_pdfs/", blank=True, null=True)

    # SEO
    meta_description = models.CharField(max_length=160, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["unit", "order"]
        unique_together = ["unit", "order"]
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        indexes = [
            models.Index(fields=["unit", "is_published"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return f"{self.unit.code} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.unit.code}-{self.title}")
        super().save(*args, **kwargs)

    def get_next_topic(self):
        """Get the next topic in the same unit."""
        try:
            return Topic.objects.filter(
                unit=self.unit, order__gt=self.order, is_published=True
            ).first()
        except Topic.DoesNotExist:
            return None

    def get_previous_topic(self):
        """Get the previous topic in the same unit."""
        try:
            return Topic.objects.filter(
                unit=self.unit, order__lt=self.order, is_published=True
            ).last()
        except Topic.DoesNotExist:
            return None


class Question(models.Model):
    """Practice questions for topics."""

    QUESTION_TYPES = [
        ("mcq", "Multiple Choice"),
        ("true_false", "True/False"),
        ("short_answer", "Short Answer"),
        ("calculation", "Calculation"),
        ("essay", "Essay"),
    ]

    DIFFICULTY_LEVELS = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="questions")

    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPES, default="mcq"
    )
    difficulty = models.CharField(
        max_length=10, choices=DIFFICULTY_LEVELS, default="medium"
    )

    question_text = models.TextField()

    # For MCQ
    option_a = models.CharField(max_length=500, blank=True)
    option_b = models.CharField(max_length=500, blank=True)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)

    correct_answer = models.CharField(
        max_length=500, help_text="Correct answer or option"
    )
    explanation = models.TextField(help_text="Explanation of the answer")

    points = models.IntegerField(default=1)
    order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["topic", "order"]
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return f"{self.topic} - Q{self.order}"


class Enrollment(models.Model):
    """Track student enrollments in levels/parts."""
    
    student = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ["student", "level", "part"]
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
        ordering = ["-enrolled_at"]
    
    def __str__(self):
        return f"{self.student.email} - {self.level} {self.part}"
    
    def get_units(self):
        """Get all units for this enrollment."""
        return Unit.objects.filter(level=self.level, part=self.part)
