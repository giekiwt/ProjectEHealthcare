from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserHealthProfileView,
    ChangePasswordView,
    UserViewSet,
    AppointmentViewSet,
    SendOTPView,
    ResetPasswordView
)

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('health-profile/', UserHealthProfileView.as_view(), name='health-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('send-otp/', SendOTPView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
    path('', include(router.urls)),
] 