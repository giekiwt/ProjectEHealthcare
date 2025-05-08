from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render
from .models import Doctor, HealthcareFacility, Appointment, Review, News
from .serializers import (
    DoctorSerializer,
    HealthcareFacilitySerializer,
    AppointmentSerializer,
    ReviewSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from .filters import HealthcareFacilityFilter, DoctorFilter
from math import radians, sin, cos, sqrt, atan2
import googlemaps
from django.conf import settings

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return distance

class DoctorListView(generics.ListCreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DoctorFilter
    search_fields = ['name', 'specialty', 'qualification']
    ordering_fields = ['name', 'specialty', 'rating']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

class HealthcareFacilityListView(generics.ListCreateAPIView):
    queryset = HealthcareFacility.objects.all()
    serializer_class = HealthcareFacilitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = HealthcareFacilityFilter
    search_fields = ['name', 'address', 'services']
    ordering_fields = ['rating', 'name', 'facility_type']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by location if provided
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = float(self.request.query_params.get('radius', 10))  # Default 10km radius
        
        if lat and lng:
            lat = float(lat)
            lng = float(lng)
            # Filter facilities within the radius
            facilities = []
            for facility in queryset:
                distance = calculate_distance(lat, lng, facility.latitude, facility.longitude)
                if distance <= radius:
                    facility.distance = distance
                    facilities.append(facility)
            # Sort by distance
            facilities.sort(key=lambda x: x.distance)
            return facilities
        
        return queryset

class HealthcareFacilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = HealthcareFacility.objects.all()
    serializer_class = HealthcareFacilitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class AppointmentView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Appointment.objects.all()
        return Appointment.objects.filter(patient=user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ReviewView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GooglePlacesSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = request.query_params.get('radius', 5000)  # Default 5km radius
        type = request.query_params.get('type', 'hospital')

        if not lat or not lng:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        
        try:
            places_result = gmaps.places_nearby(
                location=(float(lat), float(lng)),
                radius=int(radius),
                type=type,
                keyword='healthcare'
            )

            # Process and format the results
            results = []
            for place in places_result.get('results', []):
                result = {
                    'name': place.get('name'),
                    'address': place.get('vicinity'),
                    'rating': place.get('rating'),
                    'place_id': place.get('place_id'),
                    'location': {
                        'lat': place['geometry']['location']['lat'],
                        'lng': place['geometry']['location']['lng']
                    }
                }
                results.append(result)

            return Response(results)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DirectionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        origin = request.query_params.get('origin')
        destination = request.query_params.get('destination')

        if not origin or not destination:
            return Response(
                {'error': 'Origin and destination are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        
        try:
            directions_result = gmaps.directions(
                origin,
                destination,
                mode="driving"
            )

            if not directions_result:
                return Response(
                    {'error': 'No directions found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Extract relevant information
            route = directions_result[0]
            legs = route['legs'][0]
            
            result = {
                'distance': legs['distance']['text'],
                'duration': legs['duration']['text'],
                'start_address': legs['start_address'],
                'end_address': legs['end_address'],
                'steps': [
                    {
                        'instruction': step['html_instructions'],
                        'distance': step['distance']['text'],
                        'duration': step['duration']['text']
                    }
                    for step in legs['steps']
                ]
            }

            return Response(result)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def news_list(request):
    news_list = News.objects.all()
    return render(request, 'healthcare/news_list.html', {'news_list': news_list})

def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug)
    return render(request, 'healthcare/news_detail.html', {'news': news})