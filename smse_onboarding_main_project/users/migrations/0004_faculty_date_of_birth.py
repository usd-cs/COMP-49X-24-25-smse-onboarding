# Generated by Django 5.1.3 on 2025-05-05 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_faculty_dark_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='faculty',
            name='date_of_birth',
            field=models.DateTimeField(default='1990-01-01T00:00:00-08:00'),
        ),
    ]
