from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import ChatAPIView

app_name = 'chatbot'

router = DefaultRouter()
router.register(r'sessions', views.ChatSessionViewSet, basename='chat-session')

urlpatterns = [
    path('', include(router.urls)),
    path('chatbot/', ChatAPIView.as_view(), name='chatbot-api'),
] 