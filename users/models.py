from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import filters, permissions
from django.utils import timezone

class User(AbstractUser):
    GENDER_CHOICES = (
        ('M', 'Nam'),
        ('F', 'Nữ'),
        ('O', 'Khác'),
    )
    
    email = models.EmailField(_('Địa chỉ email'), unique=True)
    phone_number = models.CharField(_('Số điện thoại'), max_length=15, blank=True)
    date_of_birth = models.DateField(_('Ngày sinh'), null=True, blank=True)
    gender = models.CharField(_('Giới tính'), max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(_('Địa chỉ'), blank=True)
    profile_picture = models.ImageField(_('Ảnh đại diện'), upload_to='profile_pictures/', blank=True)
    is_verified = models.BooleanField(_('Đã xác thực'), default=False)
    created_at = models.DateTimeField(_('Ngày tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Ngày cập nhật'), auto_now=True)
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên", blank=True)
    ROLE_CHOICES = (
        ('patient', 'Bệnh nhân'),
        ('doctor', 'Bác sĩ'),
        ('admin', 'Quản trị viên'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('Người dùng')
        verbose_name_plural = _('Người dùng')

    def __str__(self):
        return self.email

class UserHealthProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_profile', verbose_name=_('Người dùng'))
    blood_type = models.CharField(_('Nhóm máu'), max_length=5, blank=True)
    height = models.DecimalField(_('Chiều cao (cm)'), max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(_('Cân nặng (kg)'), max_digits=5, decimal_places=2, null=True, blank=True)
    allergies = models.TextField(_('Dị ứng'), blank=True)
    medical_conditions = models.TextField(_('Bệnh lý'), blank=True)
    medications = models.TextField(_('Thuốc đang dùng'), blank=True)
    emergency_contact = models.CharField(_('Người liên hệ khẩn cấp'), max_length=100, blank=True)
    emergency_phone = models.CharField(_('SĐT khẩn cấp'), max_length=15, blank=True)
    created_at = models.DateTimeField(_('Ngày tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Ngày cập nhật'), auto_now=True)

    class Meta:
        verbose_name = _('Hồ sơ sức khỏe')
        verbose_name_plural = _('Hồ sơ sức khỏe')

    def __str__(self):
        return f"Hồ sơ sức khỏe của {self.user.email}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments', verbose_name=_('Bệnh nhân'))
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments', verbose_name=_('Bác sĩ'))
    appointment_date = models.DateTimeField(_('Ngày giờ hẹn'))
    symptoms = models.TextField(_('Triệu chứng'), blank=True)
    notes = models.TextField(_('Ghi chú'), blank=True)
    status = models.CharField(_('Trạng thái'), max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(_('Ngày tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Ngày cập nhật'), auto_now=True)

    class Meta:
        verbose_name = _('Lịch hẹn')
        verbose_name_plural = _('Lịch hẹn')
        ordering = ['-appointment_date']

    def __str__(self):
        return f"Lịch hẹn: {self.patient.full_name} - {self.doctor.full_name} - {self.appointment_date.strftime('%d/%m/%Y %H:%M')}"

    def is_upcoming(self):
        return self.appointment_date > timezone.now()

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)