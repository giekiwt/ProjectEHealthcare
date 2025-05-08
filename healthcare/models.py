from django.db import models
from users.models import User

class HealthcareFacility(models.Model):
    FACILITY_TYPES = (
        ('HOSPITAL', 'Hospital'),
        ('CLINIC', 'Clinic'),
        ('PHARMACY', 'Pharmacy'),
        ('LAB', 'Laboratory'),
        ('OTHER', 'Other'),
    )

    name = models.CharField(max_length=255)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPES)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    operating_hours = models.JSONField(default=dict)
    services = models.TextField(blank=True)
    image = models.ImageField(upload_to='facility_images/', blank=True, null=True)
    rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Healthcare Facilities'
        ordering = ['-rating', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_facility_type_display()})"

class Doctor(models.Model):
    SPECIALTIES = (
        ('GP', 'General Practitioner'),
        ('CARDIOLOGIST', 'Cardiologist'),
        ('DERMATOLOGIST', 'Dermatologist'),
        ('NEUROLOGIST', 'Neurologist'),
        ('PEDIATRICIAN', 'Pediatrician'),
        ('GYNECOLOGIST', 'Gynecologist'),
        ('ORTHOPEDIST', 'Orthopedist'),
        ('OTHER', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialty = models.CharField(max_length=20, choices=SPECIALTIES)
    license_number = models.CharField(max_length=50)
    years_of_experience = models.IntegerField()
    education = models.TextField()
    certifications = models.TextField(blank=True)
    facilities = models.ManyToManyField(HealthcareFacility, related_name='doctors')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return self.user.full_name  # hoặc self.user.get_full_name()

    class Meta:
        ordering = ['-rating', 'specialty', 'user__first_name']

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.get_specialty_display()})"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    facility = models.ForeignKey(HealthcareFacility, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"Appointment: {self.patient.get_full_name()} with Dr. {self.doctor.user.get_full_name()} on {self.date} at {self.time}"

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    facility = models.ForeignKey(HealthcareFacility, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.doctor if self.doctor else self.facility
        return f"Review by {self.user.get_full_name()} for {target}"

class Patient(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

class News(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title