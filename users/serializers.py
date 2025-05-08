from rest_framework import serializers
from .models import User, UserHealthProfile, Appointment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password

class UserHealthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHealthProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class UserSerializer(serializers.ModelSerializer):
    health_profile = UserHealthProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('is_verified', 'created_at', 'updated_at')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD  # Đảm bảo User model có EMAIL_FIELD = 'email'

    def validate(self, attrs):
        # Lấy email và password từ request
        email = attrs.get("email")
        password = attrs.get("password")
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password) and user.is_active:
            data = super().validate({
                "username": user.username,  # SimpleJWT vẫn cần username
                "password": password
            })
            return data
        raise serializers.ValidationError({"detail": "No active account found with the given credentials"}) 

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'patient_name', 'doctor_name', 'appointment_date', 
                 'symptoms', 'notes', 'status', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')