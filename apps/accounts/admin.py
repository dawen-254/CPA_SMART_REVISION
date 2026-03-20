"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, StudentProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin."""

    list_display = ("email", "full_name", "is_staff", "email_verified", "date_joined")
    list_filter = ("is_staff", "is_superuser", "email_verified", "date_joined")
    search_fields = ("email", "full_name", "phone_number")
    ordering = ("-date_joined",)
    readonly_fields = ("last_login", "date_joined", "updated_at")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("full_name", "phone_number")}),
        (_("Verification"), {"fields": ("email_verified", "verification_token")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "password1", "password2"),
            },
        ),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Student Profile admin."""

    list_display = ("user", "current_level", "current_part", "exam_date", "institution")
    list_filter = ("current_level", "current_part", "created_at")
    search_fields = ("user__email", "user__full_name", "institution", "student_id")
    date_hierarchy = "created_at"

    fieldsets = (
        ("User Information", {"fields": ("user",)}),
        (
            "Study Information",
            {"fields": ("current_level", "current_part", "exam_date")},
        ),
        ("Profile Details", {"fields": ("institution", "student_id", "bio", "avatar")}),
        (
            "Study Preferences",
            {"fields": ("daily_study_goal_minutes", "preferred_study_time")},
        ),
    )

    readonly_fields = ("created_at", "updated_at")
