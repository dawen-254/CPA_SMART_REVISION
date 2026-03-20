
from django.urls import path
from . import views



app_name="ai_tutor"

urlpatterns = [
    path("chat/", views.chat_view, name="chat"),
    path("chat/topic/<int:topic_id>/", views.chat_view, name="topic_chat"),
    path("send-message/", views.send_message, name="send_message"),
]
