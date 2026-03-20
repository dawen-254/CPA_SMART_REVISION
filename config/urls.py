"""
URL configuration for CPA Smart Revision project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Home
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    # Apps
    path("accounts/", include("apps.accounts.urls")),
    path("content/", include("apps.content.urls")),
    path("revision/", include("apps.revision.urls")),
    path("ai/", include("apps.ai_tutor.urls")),
    path("planner/", include("apps.planner.urls")),
    path("subscriptions/", include("apps.subscriptions.urls")),
    path("analytics/", include("apps.analytics.urls")),
    # API
    path("api/accounts/", include("apps.accounts.api_urls")),
    path("api/content/", include("apps.content.api_urls")),
    path("api/revision/", include("apps.revision.api_urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site branding
admin.site.site_header = "CPA Smart Revision Admin"
admin.site.site_title = "CPA Admin"
admin.site.index_title = "Welcome to CPA Smart Revision Administration"
