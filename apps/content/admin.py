"""
Admin configuration for content app.
"""
from django.contrib import admin
from .models import Level, Part, Unit, Topic, Question


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    min_num = 0
    fields = ('order', 'question_type', 'difficulty', 'question_text', 'is_active')
    ordering = ('order',)


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1
    fields = ('title', 'order', 'difficulty', 'is_published', 'is_premium')
    ordering = ('order',)


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "order", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("order",)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Display Order', {
            'fields': ('order',),
            'description': 'Lower numbers appear first. Set order to: Foundation=1, Intermediate=2, Advanced=3'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ("name", "level", "order")
    list_filter = ("level",)
    ordering = ("level", "order")


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "level", "part", "difficulty_level", "is_active", "get_topic_count")
    list_filter = ("level", "part", "difficulty_level", "is_active")
    search_fields = ("code", "name", "description")
    inlines = [TopicInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'level', 'part', 'order')
        }),
        ('Description & Metadata', {
            'fields': ('description', 'difficulty_level', 'estimated_hours')
        }),
        ('Media', {
            'fields': ('thumbnail', 'syllabus_file'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def get_topic_count(self, obj):
        return obj.topics.count()
    get_topic_count.short_description = 'Topics'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "unit", "order", "difficulty", "is_published", "is_premium", "get_question_count")
    list_filter = ("unit__level", "unit", "difficulty", "is_published", "is_premium")
    search_fields = ("title", "content", "unit__name")
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'unit', 'order', 'slug')
        }),
        ('Content', {
            'fields': ('content', 'summary')
        }),
        ('Learning Resources', {
            'fields': ('objectives', 'examples', 'formulas', 'references'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('video_url', 'pdf_file'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('difficulty', 'estimated_minutes', 'is_published', 'is_premium', 'meta_description')
        }),
    )
    
    readonly_fields = ('slug',)
    ordering = ('unit', 'order')
    
    def get_question_count(self, obj):
        return obj.questions.count()
    get_question_count.short_description = 'Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_type", "topic", "difficulty", "order", "points", "is_active")
    list_filter = ("question_type", "difficulty", "is_active", "topic__unit")
    search_fields = ("question_text", "topic__title")
    fieldsets = (
        ('Question Details', {
            'fields': ('topic', 'question_type', 'question_text', 'order')
        }),
        ('Options (for MCQ)', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d'),
            'classes': ('collapse',)
        }),
        ('Answer & Explanation', {
            'fields': ('correct_answer', 'explanation', 'points')
        }),
        ('Metadata', {
            'fields': ('difficulty', 'is_active')
        }),
    )
    ordering = ('topic', 'order')
