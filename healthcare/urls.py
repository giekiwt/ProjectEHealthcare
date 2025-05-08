from django.urls import path
from .views import (
    DoctorListView,
    DoctorDetailView,
    HealthcareFacilityListView,
    HealthcareFacilityDetailView,
    AppointmentView,
    ReviewView,
    GooglePlacesSearchView,
    DirectionsView
)
from . import views

urlpatterns = [
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('facilities/', HealthcareFacilityListView.as_view(), name='facility-list'),
    path('facilities/<int:pk>/', HealthcareFacilityDetailView.as_view(), name='facility-detail'),
    path('appointments/', AppointmentView.as_view(), name='appointment-list'),
    path('reviews/', ReviewView.as_view(), name='review-list'),
    path('places/search/', GooglePlacesSearchView.as_view(), name='places-search'),
    path('directions/', DirectionsView.as_view(), name='directions'),
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
]