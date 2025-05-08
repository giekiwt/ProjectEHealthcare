from django.contrib import admin
from .models import HealthcareFacility, Doctor, Appointment, Review, Patient
from django.utils.html import format_html

class HealthcareFacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'facility_type', 'address', 'phone', 'rating', 'image_tag')
    fields = ('name', 'facility_type', 'address', 'phone', 'email', 'website', 'latitude', 'longitude', 'operating_hours', 'services', 'image', 'rating', 'review_count')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" />', obj.image.url)
        else:
            return format_html('<img src="/image/hospital.jpg" width="60" />')
    image_tag.short_description = 'Ảnh'

admin.site.register(HealthcareFacility, HealthcareFacilityAdmin)

class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialty', 'license_number', 'years_of_experience', 'consultation_fee', 'rating')
    
    def full_name(self, obj):
        return obj.user.full_name  # hoặc obj.user.get_full_name()
    full_name.short_description = "Họ và tên"

admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Appointment)
admin.site.register(Review)
admin.site.register(Patient) 