from django.core.management.base import BaseCommand
from users.models import User
from healthcare.models import Doctor, HealthcareFacility
import random

SPECIALTIES = [
    ('GP', 'General Practitioner'),
    ('CARDIOLOGIST', 'Cardiologist'),
    ('DERMATOLOGIST', 'Dermatologist'),
    ('NEUROLOGIST', 'Neurologist'),
    ('PEDIATRICIAN', 'Pediatrician'),
    ('GYNECOLOGIST', 'Gynecologist'),
    ('ORTHOPEDIST', 'Orthopedist'),
    ('OTHER', 'Other'),
]

class Command(BaseCommand):
    help = 'Seed 50 sample doctors (doctor51@test.com đến doctor100@test.com)'

    def handle(self, *args, **kwargs):
        facilities = list(HealthcareFacility.objects.all())
        if not facilities:
            self.stdout.write(self.style.ERROR('Bạn cần tạo ít nhất 1 cơ sở vật chất trước!'))
            return

        created = 0
        for i in range(51, 101):  # doctor51@test.com đến doctor100@test.com
            email = f'doctor{i}@test.com'
            if User.objects.filter(email=email).exists():
                continue
            user = User.objects.create_user(
                email=email,
                username=f'doctor{i}',
                password='Test123456',
                full_name=f'Bác sĩ Số {i}'
            )
            specialty, _ = random.choice(SPECIALTIES)
            doctor = Doctor.objects.create(
                user=user,
                specialty=specialty,
                license_number=f'LIC-{1000+i}',
                years_of_experience=random.randint(1, 30),
                education=f'Bằng cấp chuyên ngành {specialty}',
                certifications='Chứng chỉ A\nChứng chỉ B\nChứng chỉ C',
                consultation_fee=random.randint(200000, 1000000),
            )
            doctor.facilities.set(random.sample(facilities, k=random.randint(1, min(2, len(facilities)))))
            doctor.save()
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Đã tạo mới {created} bác sĩ mẫu (từ doctor51@test.com đến doctor100@test.com)!')) 