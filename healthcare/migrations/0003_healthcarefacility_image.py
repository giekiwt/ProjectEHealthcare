# Generated by Django 5.2 on 2025-05-05 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0002_patient'),
    ]

    operations = [
        migrations.AddField(
            model_name='healthcarefacility',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='facility_images/'),
        ),
    ]
