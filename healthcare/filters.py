from django_filters import rest_framework as filters
from .models import HealthcareFacility, Doctor

class HealthcareFacilityFilter(filters.FilterSet):
    min_rating = filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name='rating', lookup_expr='lte')
    facility_type = filters.CharFilter(field_name='facility_type')
    services = filters.CharFilter(field_name='services', lookup_expr='icontains')

    class Meta:
        model = HealthcareFacility
        fields = ['facility_type', 'min_rating', 'max_rating', 'services']

class DoctorFilter(filters.FilterSet):
    min_rating = filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name='rating', lookup_expr='lte')
    specialty = filters.CharFilter(field_name='specialty')
    min_experience = filters.NumberFilter(field_name='years_of_experience', lookup_expr='gte')
    max_fee = filters.NumberFilter(field_name='consultation_fee', lookup_expr='lte')
    facility = filters.NumberFilter(field_name='facilities')

    class Meta:
        model = Doctor
        fields = ['specialty', 'min_rating', 'max_rating', 'min_experience', 'max_fee', 'facility'] 