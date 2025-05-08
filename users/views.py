from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import User, UserHealthProfile, Appointment, PasswordResetOTP
from healthcare.models import Doctor
from .serializers import UserSerializer, UserHealthProfileSerializer, MyTokenObtainPairSerializer, AppointmentSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
import random
from datetime import timedelta

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        # Send verification email
        # send_verification_email(user)

def send_verification_email(user):
    token = RefreshToken.for_user(user).access_token
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}/"
    subject = 'Verify your email address'
    message = f'Click the following link to verify your email: {verification_url}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])

class UserLoginView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        print("EMAIL:", email)
        print("PASSWORD:", password)
        user = User.objects.filter(email=email).first()
        print("USER:", user)
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class UserHealthProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserHealthProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserHealthProfile.objects.get_or_create(user=self.request.user)
        return profile

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response(
                {'error': 'Wrong password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password updated successfully'})

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [AllowAny]  # hoặc quyền phù hợp 

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer 

# Tạo user role doctor
# user = User.objects.create(email="abc@gmail.com", role="doctor", ...)

# Tạo Doctor profile
# doctor = Doctor.objects.create(user=user, specialty="CARDIOLOGIST", ...)

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'doctor':
            return Appointment.objects.filter(doctor=user)
        return Appointment.objects.filter(patient=user)

    def perform_create(self, serializer):
        # Automatically set the patient as the current user if they're a patient
        if self.request.user.role == 'patient':
            serializer.save(patient=self.request.user)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def upcoming(self):
        now = timezone.now()
        appointments = self.get_queryset().filter(
            appointment_date__gt=now,
            status__in=['pending', 'confirmed']
        ).order_by('appointment_date')
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self):
        now = timezone.now()
        appointments = self.get_queryset().filter(
            appointment_date__lt=now
        ).order_by('-appointment_date')
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        if appointment.status == 'completed':
            return Response(
                {'error': 'Cannot cancel a completed appointment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        appointment.status = 'cancelled'
        appointment.save()
        return Response({'status': 'appointment cancelled'})

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        if request.user.role != 'doctor' or request.user != appointment.doctor:
            return Response(
                {'error': 'Only the assigned doctor can confirm appointments'},
                status=status.HTTP_403_FORBIDDEN
            )
        if appointment.status != 'pending':
            return Response(
                {'error': 'Can only confirm pending appointments'},
                status=status.HTTP_400_BAD_REQUEST
            )
        appointment.status = 'confirmed'
        appointment.save()
        return Response({'status': 'appointment confirmed'})

class SendOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Email không tồn tại!'}, status=400)
        otp = str(random.randint(100000, 999999))
        PasswordResetOTP.objects.create(user=user, otp=otp)
        send_mail(
            'Mã OTP đặt lại mật khẩu',
            f'Mã OTP của bạn là: {otp}',
            None,
            [email],
        )
        return Response({'message': 'Đã gửi OTP về email!'})

class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        try:
            user = User.objects.get(email=email)
            otp_obj = PasswordResetOTP.objects.filter(
                user=user, otp=otp, is_used=False,
                created_at__gte=timezone.now()-timedelta(minutes=10)
            ).last()
            if not otp_obj:
                return Response({'error': 'OTP không hợp lệ hoặc đã hết hạn!'}, status=400)
            user.set_password(new_password)
            user.save()
            otp_obj.is_used = True
            otp_obj.save()
            return Response({'message': 'Đặt lại mật khẩu thành công!'})
        except User.DoesNotExist:
            return Response({'error': 'Email không tồn tại!'}, status=400)