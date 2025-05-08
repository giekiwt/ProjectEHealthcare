from django.core.management.base import BaseCommand
from healthcare.models import HealthcareFacility
import random

FACILITY_TYPES = [
    'HOSPITAL',
    'CLINIC',
    'PHARMACY',
    'LAB',
    'OTHER',
]

ADDRESSES = [
    "123 Lê Lợi, Quận 1, TP.HCM",
    "456 Nguyễn Trãi, Quận 5, TP.HCM",
    "789 Trần Hưng Đạo, Quận 1, TP.HCM",
    "12 Nguyễn Văn Cừ, Quận 10, TP.HCM",
    "34 Lý Thường Kiệt, Quận Tân Bình, TP.HCM",
    "56 Cách Mạng Tháng 8, Quận 3, TP.HCM",
    "78 Điện Biên Phủ, Quận Bình Thạnh, TP.HCM",
    "90 Võ Thị Sáu, Quận 3, TP.HCM",
    "21 Phan Đăng Lưu, Quận Phú Nhuận, TP.HCM",
    "43 Hoàng Văn Thụ, Quận Tân Bình, TP.HCM",
]

class Command(BaseCommand):
    help = 'Seed 50 sample healthcare facilities'

    def handle(self, *args, **kwargs):
        created = 0
        for i in range(1, 51):
            name = f"Cơ sở y tế số {i}"
            if HealthcareFacility.objects.filter(name=name).exists():
                continue
            facility = HealthcareFacility.objects.create(
                name=name,
                facility_type=random.choice(FACILITY_TYPES),
                address=random.choice(ADDRESSES),
                phone=f"090{random.randint(1000000, 9999999)}",
                email=f"facility{i}@test.com",
                website=f"https://facility{i}.com",
                latitude=10.7 + random.uniform(-0.1, 0.1),
                longitude=106.6 + random.uniform(-0.1, 0.1),
                operating_hours={"mon-fri": "07:00-17:00", "sat": "07:00-12:00"},
                services="Khám bệnh, Xét nghiệm, Tư vấn sức khỏe",
                rating=round(random.uniform(3.0, 5.0), 1),
                review_count=random.randint(0, 100),
                image='image/hospital.jpg',
            )
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Đã tạo mới {created} cơ sở y tế mẫu!'))
