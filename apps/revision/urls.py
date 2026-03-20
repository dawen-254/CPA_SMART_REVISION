from django.urls import path
from . import views

app_name = 'revision'

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('topic/<slug:topic_slug>/', views.topic_detail, name='topic_detail'),
    path('flashcards/topic/<int:topic_id>/', views.flashcard_study_view, name='flashcard_study'),
    path('flashcards/generate/<int:topic_id>/', views.generate_flashcards_view, name='generate_flashcards'),
]
