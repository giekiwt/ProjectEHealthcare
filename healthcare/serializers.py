from rest_framework import serializers
from .models import HealthcareFacility, Doctor, Appointment, Review
from users.serializers import UserSerializer

class HealthcareFacilitySerializer(serializers.ModelSerializer):
    distance = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = HealthcareFacility
        fields = '__all__'
        read_only_fields = ('rating', 'review_count', 'created_at', 'updated_at')

class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    specialty_display = serializers.CharField(source='get_specialty_display', read_only=True)
    facilities = HealthcareFacilitySerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.user.profile_picture:
            url = obj.user.profile_picture.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None

    class Meta:
        model = Doctor
        fields = '__all__'
        read_only_fields = ('rating', 'review_count', 'created_at', 'updated_at')

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    facility_name = serializers.CharField(source='facility.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('patient', 'created_at', 'updated_at')

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True, required=False)
    facility_name = serializers.CharField(source='facility.name', read_only=True, required=False)
    rating_display = serializers.CharField(source='get_rating_display', read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def validate(self, data):
        if not data.get('doctor') and not data.get('facility'):
            raise serializers.ValidationError("Either doctor or facility must be specified")
        if data.get('doctor') and data.get('facility'):
            raise serializers.ValidationError("Cannot review both doctor and facility at the same time")
        return data 