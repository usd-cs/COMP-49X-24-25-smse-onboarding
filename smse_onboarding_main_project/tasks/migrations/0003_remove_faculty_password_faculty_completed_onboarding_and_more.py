# Generated by Django 5.1.3 on 2025-02-19 19:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_faculty_otheremployee_facultydocument_taskprogress'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='faculty',
            name='password',
        ),
        migrations.AddField(
            model_name='faculty',
            name='completed_onboarding',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='faculty',
            name='user',
            field=models.OneToOneField(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='faculty_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='task',
            name='assigned_to',
            field=models.ManyToManyField(blank=True, related_name='tasks', to='tasks.faculty'),
        ),
        migrations.AlterField(
            model_name='faculty',
            name='email',
            field=models.EmailField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='faculty',
            name='zoom_phone',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
