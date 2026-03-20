from django.urls import path
from . import views

app_name = "content"

urlpatterns = [
    path("units/", views.unit_list, name="unit_list"),
    path("level/<int:level_id>/<str:part_name>/", views.level_detail, name="level_detail"),
    path("unit/<slug:unit_slug>/", views.unit_detail, name="unit_detail"),
    path("enroll/<int:level_id>/<str:part_name>/", views.enroll, name="enroll"),
    path("unenroll/<int:enrollment_id>/", views.unenroll, name="unenroll"),
    path("search/", views.search_enrolled_content, name="search"),
]
